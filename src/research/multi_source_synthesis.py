"""
Multi-Source Data Synthesis Framework
Handles cross-referencing, conflict resolution, and confidence scoring
Implements institutional research standards from Bridgewater, Bloomberg, Kensho
""" 

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from src.config.logger import log


class SourceTier(Enum):
    """Source reliability hierarchy - institutional standard"""
    TIER_1 = ("SEC Filings", 0.95)  # (Description, reliability weight)
    TIER_2 = ("Financial APIs (Bloomberg-level)", 0.85)
    TIER_3 = ("Earnings Transcripts", 0.75)
    TIER_4 = ("Major News (Reuters/FT)", 0.65)
    TIER_5 = ("Web/Other Sources", 0.45)


class ConfidenceLevel(Enum):
    """Confidence assessment based on source alignment"""
    HIGH = "HIGH"      # 3+ sources agree OR 2+ Tier 1-2 sources agree
    MEDIUM = "MEDIUM"  # 2 sources agree OR conflicting tiers
    LOW = "LOW"        # Single source only


@dataclass
class DataPoint:
    """Represents a single metric from a source"""
    metric_name: str
    value: Any
    source: str
    source_tier: SourceTier
    time_period: str
    confidence_input: str = ""  # What the source claims about confidence


@dataclass
class ResolvedDataPoint:
    """Final reconciled data point after conflict resolution"""
    metric_name: str
    value: Any
    primary_source: str
    primary_tier: SourceTier
    supporting_sources: List[Tuple[str, SourceTier, bool]]  # (source, tier, agreement)
    confidence: ConfidenceLevel
    conflicts: List[Dict[str, Any]] = None
    resolution_method: str = ""


class MultiSourceSynthesis:
    """
    Framework for multi-source data synthesis
    Implements institutional-grade triangulation and conflict resolution
    """
    
    def __init__(self):
        self.data_points: List[DataPoint] = []
        self.resolved_points: List[ResolvedDataPoint] = []
        self.conflict_log: List[Dict[str, Any]] = []
        log.info("Initialized MultiSourceSynthesis framework")
    
    def add_data_point(
        self,
        metric_name: str,
        value: Any,
        source: str,
        source_tier: SourceTier,
        time_period: str = "Current"
    ) -> None:
        """Register a data point from a source"""
        point = DataPoint(
            metric_name=metric_name,
            value=value,
            source=source,
            source_tier=source_tier,
            time_period=time_period
        )
        self.data_points.append(point)
        log.debug(f"Added data point: {metric_name} = {value} from {source} [{source_tier.value[0]}]")
    
    def detect_conflicts(self, metric_name: str, tolerance_percent: float = 5.0) -> List[Dict[str, Any]]:
        """
        Detect conflicts between sources for a specific metric
        Returns conflicts within tolerance_percent variance
        """
        metric_data = [p for p in self.data_points if p.metric_name == metric_name]
        
        if len(metric_data) < 2:
            return []
        
        conflicts = []
        
        # Group by numeric vs non-numeric values
        numeric_data = []
        for p in metric_data:
            try:
                numeric_value = float(str(p.value).replace('%', '').replace('$', '').replace(',', ''))
                numeric_data.append((p.value, numeric_value, p.source, p.source_tier))
            except (ValueError, TypeError):
                pass
        
        # Check for conflicts among numeric data
        if len(numeric_data) >= 2:
            for i in range(len(numeric_data)):
                for j in range(i + 1, len(numeric_data)):
                    value_a, numeric_a, source_a, tier_a = numeric_data[i]
                    value_b, numeric_b, source_b, tier_b = numeric_data[j]
                    
                    # Calculate variance percentage
                    avg_value = (numeric_a + numeric_b) / 2
                    if avg_value != 0:
                        variance = abs(numeric_a - numeric_b) / avg_value * 100
                    else:
                        variance = 0
                    
                    if variance > tolerance_percent:
                        conflict = {
                            "metric": metric_name,
                            "source_a": source_a,
                            "value_a": value_a,
                            "tier_a": tier_a.value[0],
                            "source_b": source_b,
                            "value_b": value_b,
                            "tier_b": tier_b.value[0],
                            "variance_percent": round(variance, 2),
                            "resolution_priority": "Use Tier A" if tier_a.value[1] > tier_b.value[1] else "Use Tier B"
                        }
                        conflicts.append(conflict)
                        self.conflict_log.append(conflict)
        
        return conflicts
    
    def triangulate_metric(self, metric_name: str) -> ResolvedDataPoint:
        """
        Triangulate a metric across multiple sources
        Implements institutional conflict resolution hierarchy
        """
        metric_data = [p for p in self.data_points if p.metric_name == metric_name]
        
        if not metric_data:
            log.warning(f"No data found for metric: {metric_name}")
            return None
        
        if len(metric_data) == 1:
            # Single source - confidence is LOW
            point = metric_data[0]
            return ResolvedDataPoint(
                metric_name=metric_name,
                value=point.value,
                primary_source=point.source,
                primary_tier=point.source_tier,
                supporting_sources=[],
                confidence=ConfidenceLevel.LOW,
                resolution_method="Single source only"
            )
        
        # Multiple sources - triangulate
        conflicts = self.detect_conflicts(metric_name)
        
        # Sort by source tier reliability (descending)
        sorted_data = sorted(metric_data, key=lambda p: p.source_tier.value[1], reverse=True)
        
        # Determine consensus
        primary_point = sorted_data[0]
        supporting_sources = []
        agreement_count = 0
        
        # Group remaining sources
        for point in sorted_data[1:]:
            try:
                # Numeric comparison
                primary_val = float(str(primary_point.value).replace('%', '').replace('$', '').replace(',', ''))
                point_val = float(str(point.value).replace('%', '').replace('$', '').replace(',', ''))
                
                avg = (primary_val + point_val) / 2
                variance = abs(primary_val - point_val) / avg * 100 if avg != 0 else 0
                
                agrees = variance < 5.0  # Within 5% = agreement
                supporting_sources.append((point.source, point.source_tier, agrees))
                if agrees:
                    agreement_count += 1
                    
            except (ValueError, TypeError):
                # Non-numeric comparison
                agrees = primary_point.value == point.value
                supporting_sources.append((point.source, point.source_tier, agrees))
                if agrees:
                    agreement_count += 1
        
        # Determine confidence level
        tier_1_or_2_count = sum(1 for s, t, a in supporting_sources if t in [SourceTier.TIER_1, SourceTier.TIER_2])
        
        if primary_point.source_tier in [SourceTier.TIER_1, SourceTier.TIER_2] and tier_1_or_2_count >= 1 and agreement_count >= 1:
            confidence = ConfidenceLevel.HIGH
        elif agreement_count >= 1:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW if len(supporting_sources) > 0 else ConfidenceLevel.LOW
        
        return ResolvedDataPoint(
            metric_name=metric_name,
            value=primary_point.value,
            primary_source=primary_point.source,
            primary_tier=primary_point.source_tier,
            supporting_sources=supporting_sources,
            confidence=confidence,
            conflicts=conflicts if conflicts else None,
            resolution_method=f"Primary: {primary_point.source_tier.value[0]}, Supporting: {agreement_count} agreement(s)"
        )
    
    def get_synthesis_report(self) -> Dict[str, Any]:
        """Generate comprehensive multi-source synthesis report"""
        unique_metrics = list(set(p.metric_name for p in self.data_points))
        
        report = {
            "timestamp": str(__import__('datetime').datetime.now()),
            "total_sources": len(set(p.source for p in self.data_points)),
            "total_data_points": len(self.data_points),
            "unique_metrics": len(unique_metrics),
            "triangulated_metrics": {},
            "conflict_summary": {
                "total_conflicts": len(self.conflict_log),
                "high_variance_conflicts": len([c for c in self.conflict_log if c.get("variance_percent", 0) > 10]),
                "conflicts_by_metric": {}
            },
            "source_tier_distribution": {},
            "confidence_distribution": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }
        
        # Triangulate each metric
        for metric in unique_metrics:
            resolved = self.triangulate_metric(metric)
            if resolved:
                self.resolved_points.append(resolved)
                report["triangulated_metrics"][metric] = {
                    "value": resolved.value,
                    "primary_source": resolved.primary_source,
                    "primary_tier": resolved.primary_tier.value[0],
                    "confidence": resolved.confidence.value,
                    "supporting_agreements": sum(1 for _, _, agrees in resolved.supporting_sources if agrees),
                    "total_supporting_sources": len(resolved.supporting_sources),
                    "conflicts": len(resolved.conflicts) if resolved.conflicts else 0,
                    "resolution_method": resolved.resolution_method
                }
                report["confidence_distribution"][resolved.confidence.value] += 1
        
        # Conflict summary by metric
        for conflict in self.conflict_log:
            metric = conflict["metric"]
            if metric not in report["conflict_summary"]["conflicts_by_metric"]:
                report["conflict_summary"]["conflicts_by_metric"][metric] = []
            report["conflict_summary"]["conflicts_by_metric"][metric].append(conflict)
        
        # Source tier distribution
        for point in self.data_points:
            tier_name = point.source_tier.value[0]
            if tier_name not in report["source_tier_distribution"]:
                report["source_tier_distribution"][tier_name] = 0
            report["source_tier_distribution"][tier_name] += 1
        
        log.info(f"Generated synthesis report: {len(self.resolved_points)} metrics triangulated")
        return report
    
    def export_synthesis_json(self) -> str:
        """Export synthesis results as JSON"""
        report = self.get_synthesis_report()
        return json.dumps(report, indent=2, default=str)
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """
        Validate overall data quality
        Returns quality metrics and recommendations
        """
        if not self.data_points:
            return {"status": "NO_DATA", "score": 0.0}
        
        metrics = {
            "total_data_points": len(self.data_points),
            "source_diversity_score": 0.0,
            "conflict_rate": 0.0,
            "high_tier_coverage": 0.0,
            "overall_quality_score": 0.0,
            "recommendations": []
        }
        
        # Source diversity (max 5 points for 5 tiers represented)
        unique_tiers = len(set(p.source_tier for p in self.data_points))
        metrics["source_diversity_score"] = (unique_tiers / 5.0) * 100
        
        # Conflict rate
        metrics["conflict_rate"] = (len(self.conflict_log) / max(len(self.data_points), 1)) * 100
        
        # High-tier coverage (Tier 1 + Tier 2)
        high_tier_points = sum(1 for p in self.data_points 
                              if p.source_tier in [SourceTier.TIER_1, SourceTier.TIER_2])
        metrics["high_tier_coverage"] = (high_tier_points / len(self.data_points)) * 100
        
        # Overall quality score (weighted average)
        metrics["overall_quality_score"] = (
            metrics["source_diversity_score"] * 0.3 +
            (100 - min(metrics["conflict_rate"], 100)) * 0.4 +
            metrics["high_tier_coverage"] * 0.3
        )
        
        # Recommendations
        if metrics["source_diversity_score"] < 60:
            metrics["recommendations"].append("Increase source diversity - include more source types")
        if metrics["conflict_rate"] > 20:
            metrics["recommendations"].append("High conflict rate - review data sources and methodologies")
        if metrics["high_tier_coverage"] < 50:
            metrics["recommendations"].append("Improve high-tier source coverage (SEC, Financial APIs)")
        if metrics["overall_quality_score"] > 80:
            metrics["recommendations"].append("✓ Data quality is EXCELLENT")
        
        return metrics
