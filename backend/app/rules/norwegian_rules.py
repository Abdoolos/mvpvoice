"""
Norwegian telecom sales compliance rules engine.
Designer: Abdullah Alawiss
"""

from typing import Dict, Any, List
from ..workers.analysis_tasks import (
    check_bindingstid_compliance,
    check_price_compliance,
    check_pressure_compliance
)

class NorwegianRulesEngine:
    """Rules engine for Norwegian telecom sales compliance."""
    
    def analyze_transcript(self, text: str, segments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze transcript for Norwegian telecom compliance.
        Returns comprehensive analysis results.
        """
        
        # Run all compliance checks
        bindingstid_result = check_bindingstid_compliance.delay(0, text).get()
        pris_result = check_price_compliance.delay(0, text).get()
        press_result = check_pressure_compliance.delay(0, text).get()
        
        # Collect all violations
        all_violations = []
        all_violations.extend(bindingstid_result["violations"])
        all_violations.extend(pris_result["violations"])
        all_violations.extend(press_result["violations"])
        
        # Generate summary
        summary = self._generate_summary(bindingstid_result, pris_result, press_result, all_violations)
        
        # Extract key points
        key_points = self._extract_key_points(text, all_violations)
        
        return {
            "bindingstid": {
                "mentioned": bindingstid_result["mentioned"],
                "details": bindingstid_result["details"]
            },
            "pris": {
                "mentioned": pris_result["mentioned"],
                "details": pris_result["details"]
            },
            "press": {
                "mentioned": press_result["mentioned"],
                "details": press_result["details"]
            },
            "violations": all_violations,
            "summary": summary,
            "key_points": key_points
        }
    
    def _generate_summary(self, bindingstid: Dict, pris: Dict, press: Dict, violations: List) -> str:
        """Generate analysis summary in Norwegian."""
        
        if not violations:
            return "Samtalen følger alle nødvendige retningslinjer for telecom-salg. Bindingstid og priser er tydelig kommunisert, og det er ikke brukt utilbørlige salgsteknikker."
        
        summary_parts = []
        
        # Bindingstid issues
        if not bindingstid["mentioned"]:
            summary_parts.append("Bindingstid ikke nevnt")
        elif any(v["type"] == "bindingstid_unclear" for v in violations):
            summary_parts.append("Bindingstid nevnt men ikke klart kommunisert")
        
        # Price issues
        if not pris["mentioned"]:
            summary_parts.append("Prisinformasjon mangler")
        elif any(v["type"] == "price_incomplete" for v in violations):
            summary_parts.append("Ufullstendig prisinformasjon")
        
        # Pressure issues
        pressure_violations = [v for v in violations if "pressure" in v["type"] or "urgency" in v["type"]]
        if pressure_violations:
            summary_parts.append("Utilbørlige salgsteknikker oppdaget")
        
        if summary_parts:
            return f"Regelbrudd funnet: {', '.join(summary_parts)}. Samtalen følger ikke retningslinjene for ansvarlig telecom-salg."
        else:
            return "Mindre problemer funnet, men hovedkravene er oppfylt."
    
    def _extract_key_points(self, text: str, violations: List) -> List[str]:
        """Extract key points from the conversation."""
        
        key_points = []
        
        # Check for positive elements
        if "velkommen" in text.lower() or "takk" in text.lower():
            key_points.append("Høflig tone i samtalen")
        
        if "spørsmål" in text.lower():
            key_points.append("Kunden oppfordret til å stille spørsmål")
        
        if "betingelser" in text.lower() or "vilkår" in text.lower():
            key_points.append("Vilkår og betingelser diskutert")
        
        # Add violation summaries
        high_severity_violations = [v for v in violations if v.get("severity") == "high"]
        if high_severity_violations:
            key_points.append(f"{len(high_severity_violations)} alvorlige regelbrudd funnet")
        
        medium_severity_violations = [v for v in violations if v.get("severity") == "medium"]
        if medium_severity_violations:
            key_points.append(f"{len(medium_severity_violations)} mindre regelbrudd funnet")
        
        if not violations:
            key_points.append("Ingen regelbrudd funnet")
        
        return key_points[:5]  # Limit to 5 key points
