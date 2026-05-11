"""Research module - multi-source data synthesis and triangulation"""

from .multi_source_synthesis import (
    MultiSourceSynthesis,
    SourceTier,
    ConfidenceLevel,
    DataPoint,
    ResolvedDataPoint
)

__all__ = [
    'MultiSourceSynthesis',
    'SourceTier',
    'ConfidenceLevel',
    'DataPoint',
    'ResolvedDataPoint'
]
