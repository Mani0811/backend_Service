import json
import datetime
from pathlib import Path
 
 
class PrivacyComplianceScorer:
    def __init__(self, data):
        # Load data from JSON file
        self.data = data
        self.metadata = data.get("metadata", {})
        self.parameters = {}

    # ------------------ Banner Quality Scoring ------------------
    def calculate_banner_quality(self, pre_consent_cookies_fire):
        banner_info = self.data.get("banner_analysis", {})
        exists = banner_info.get("consent_banner_existance", {}).get("exists", False)
        clarity = banner_info.get("consent_banner_quality", {}).get("language_clarity", False)
        manipulative = banner_info.get("consent_banner_quality", {}).get("manipulative_wording", False)
        buttons = banner_info.get("granular_controls", {})
        has_accept = buttons.get("accept_all_button_presence", False)
        has_reject = buttons.get("reject_all_button_presence", False)
        has_manage = buttons.get("manage_preferences_button_presence", False)
        score = 0
        if exists: score += 0.50
        else: score -= 1
        if clarity: score += 0.25
        if manipulative: score -= 0.10
 
        if has_accept and has_reject and has_manage:
            score += 0.25
        elif has_accept or has_reject or has_manage:
            score += 0.10
        else:
            score -=0.25
 
        # Visual equality placeholder (no score now)
        score += 0.0
 
        # Clamp to 0–1
        score = max(min(score, 1.0), 0.0)
 
        # Pre-consent cookies penalty – cap
        if pre_consent_cookies_fire and score > 0.75:
            score = 0.75
 
        self.parameters["banner_quality_score"] = round(score, 2)
        return score
 
    # ------------------ Long-lived Cookie Check ------------------
    def check_long_lived_cookies(self, cookies_list, threshold_days=183):
        long_lived_count = 0
        cookie_details = []
        now_dt = datetime.datetime.utcnow()
 
        for c in cookies_list:
            exp = c.get("expires")
            if not exp:
                continue
 
            if exp > 1e12:  # milliseconds
                exp /= 1000
            expiry_dt = datetime.datetime.utcfromtimestamp(exp)
 
            set_time = now_dt
            # if set time given in cookie, adjust here if needed
 
            lifespan_days = (expiry_dt - set_time).total_seconds() / 86400
            lifespan_days = max(lifespan_days, 0)
 
            cookie_details.append({
                "name": c.get("name"),
                "expiry_date": expiry_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "lifespan_days": round(lifespan_days, 2),
                "long_lived": lifespan_days > threshold_days
            })
 
            if lifespan_days > threshold_days:
                long_lived_count += 1
 
        penalty = 0.05 if long_lived_count > 0 else 0.0
        self.parameters["cookie_expiry_report"] = cookie_details
        self.parameters["long_lived_cookie_count"] = long_lived_count
        return penalty

    def calculate_expiry_score(self, cookies_list, threshold_days=183):
        """Return fraction of cookies with lifespan ≤ threshold_days."""
        now = datetime.datetime.utcnow()
        total = len(cookies_list)
        if total == 0:
            return 1.0
        short_lived = 0
        for c in cookies_list:
            exp = c.get("expires")
            if not exp:
                continue
            if exp > 1e12:
                exp /= 1000
            expiry_dt = datetime.datetime.utcfromtimestamp(exp)
            lifespan_days = max((expiry_dt - now).total_seconds() / 86400, 0)
            if lifespan_days <= threshold_days:
                short_lived += 1
        return round(short_lived / total, 2)

    def calculate_domain_score(self, cookies_list, first_party_domain):
        """Return fraction of cookies set on the first-party domain."""
        total = len(cookies_list)
        if total == 0:
            return 1.0
        first_party = sum(
            1 for c in cookies_list
            if first_party_domain in (c.get("domain") or "")
        )
        return round(first_party / total, 2)

    # ------------------ Final Score Calculation ------------------
    def calculate_score(self):
        # 1. Consent Mechanism
        before_summary = self.data.get("before_consent", {}).get("cookie_category_summary", {})
        after_summary = self.data.get("after_consent", {}).get("cookie_category_summary", {})
        
        pre_consent_cookies_fire = (
            sum(before_summary.values()) == sum(after_summary.values()) and
            sum(before_summary.values()) > 0
        )
        consent_score = self.calculate_banner_quality(pre_consent_cookies_fire)
        print("consent_score", consent_score)
        
        # 2. Cookie Classification
        cookie_summary_after = self.data.get("after_consent", {}).get("cookie_category_summary", {})
        total_non_firstparty_cookies_before= sum(before_summary.values())-cookie_summary_after.get("uncategorized", 0)
        cookie_summary_before = self.data.get("before_consent", {}).get("cookie_category_summary", {})
        total_non_firstparty_cookies_after= sum(before_summary.values())-cookie_summary_before.get("uncategorized", 0)
        if total_non_firstparty_cookies_before == total_non_firstparty_cookies_after:
            cookie_score=1
        else:
            cookie_score=.9
        print("cookie_score", cookie_score)
        # 3. Third-Party Tracking
        tracking_requests = self.data.get("network_requests", [])
        total_requests = len(tracking_requests)
        tracking_score = 1.0
        if total_requests == 0:
            tracking_score = 1.0
        else:
            advertising_count = sum(
                1
                for req in tracking_requests
                if req.get("_tracker", {}).get("category", "").lower() == "advertising"
            )
            social_count = sum(
                1
                for req in tracking_requests
                if req.get("_tracker", {}).get("category", "").lower() == "social"
            )
            FingerprintingInvasive_count = sum(
                1
                for req in tracking_requests
                if req.get("_tracker", {}).get("category", "").lower() == "fingerprinting invasive"
            )

            
            # ratio of tracker requests
            if(advertising_count+social_count+FingerprintingInvasive_count>0):
                tracker_ratio = (advertising_count + social_count + FingerprintingInvasive_count+FingerprintingInvasive_count) / total_requests
                tracking_score = 1.0 - tracker_ratio

        print("tracking_score", tracking_score)
        # # 4. Transparency
        # contact = self.data.get("bcti_data", {}).get("contactemail", "")
        # transparency_score = 1.0 if contact and "redacted" not in contact.lower() else 0.8
        # print("transparency_score", transparency_score)

        # # 5. Security
        # security_score = 1.0 if all(
        #     req.get("url", "").startswith("https://")
        #     for req in tracking_requests
        # ) else 0.9
        # print("security_score",security_score)
        # 6. Breach History

        breach_history = self.data.get("breach_data", [])
        breach_score = max(1.0 - 0.1 * len(breach_history), 0.0)
        print("breach_score", breach_score)
        # Prepare cookie list for new metrics
        before_cookies = self.data.get("before_consent", {}).get("cookies", [])
        after_cookies = self.data.get("after_consent", {}).get("cookies", [])
        all_cookies = before_cookies + after_cookies

        # 7. Cookie Expiry Score
        expiry_score = self.calculate_expiry_score(all_cookies)

        # # 8. Cookie Domain Score
        # first_party_domain = self.metadata.get("url", "")
        # domain_score = self.calculate_domain_score(all_cookies, first_party_domain)

        # Define weights (must sum to 1.0)
        weights = {
            "consent":      0.25,
            "cookies":      0.25,
            "tracking":     0.25,
            # "transparency": 0.10,
            # "security":     0.10,
            "breach":       0.15,
            "expiry":       0.10,
            # "domain":       0.15,
        }

        # Weighted average calculation
        combined_score = (
            consent_score      * weights["consent"] +
            cookie_score       * weights["cookies"] +
            tracking_score     * weights["tracking"] +
            # transparency_score * weights["transparency"] +
            # security_score     * weights["security"] +
            breach_score       * weights["breach"] +
            expiry_score       * weights["expiry"] 
            # domain_score       * weights["domain"]
        )

        # Update metadata and parameters
        self.metadata["compliance_score"] = round(combined_score * 100, 2)
        self.metadata["expiry_score"]     = expiry_score
        #self.metadata["domain_score"]     = domain_score
        self.parameters["expiry_score"]   = expiry_score
        # self.parameters["domain_score"]   = domain_score

        return self.metadata["compliance_score"]

 
    # ------------------ Save Updated JSON ------------------
    def save_json(self, output_path):
        updated_data = {
            "metadata": self.metadata,
            "parameters": self.parameters
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, indent=4)