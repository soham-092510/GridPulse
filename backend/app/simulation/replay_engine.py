import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

class ReplayEngine:
    """
    Minute-by-minute streaming replay engine for historical CSV or database records.
    Allows testing baseline learning and anomaly handling against real past data.
    """
    
    def __init__(self):
        self.records: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.is_playing: bool = False
        self.speed_multiplier: int = 10 # 1x, 10x, 60x
        
    def load_records(self, records: List[Dict[str, Any]]):
        """Loads a sequence of chronological records for playback."""
        self.records = records
        self.current_index = 0
        self.is_playing = False
        
    def load_from_dataframe(self, df: pd.DataFrame):
        records = df.to_dict(orient="records")
        self.load_records(records)

    def play(self, speed: int = 10):
        self.speed_multiplier = speed
        self.is_playing = True

    def pause(self):
        self.is_playing = False

    def step(self) -> Optional[Dict[str, Any]]:
        """Advances playback by one record and returns the payload."""
        if not self.records or self.current_index >= len(self.records):
            self.is_playing = False
            return None
            
        record = self.records[self.current_index]
        self.current_index += 1
        return record

    def get_status(self) -> Dict[str, Any]:
        return {
            "total_records": len(self.records),
            "current_index": self.current_index,
            "progress_pct": round((self.current_index / max(1, len(self.records))) * 100.0, 1),
            "is_playing": self.is_playing,
            "speed_multiplier": self.speed_multiplier
        }

replay_engine = ReplayEngine()
