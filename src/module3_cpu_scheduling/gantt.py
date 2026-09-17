"""
ASCII Gantt Chart Renderer and Timeline Visualizer
Tracks CPU execution blocks and explicit idle intervals with accurate timeline marks.
"""

from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GanttSegment:
    start_time: int
    end_time: int
    pid: str

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time

    @property
    def is_idle(self) -> bool:
        return self.pid == "[IDLE]"

class GanttChart:
    def __init__(self):
        self.segments: List[GanttSegment] = []

    def add_segment(self, start_time: int, end_time: int, pid: str):
        if end_time <= start_time:
            return  # No zero or negative interval
            
        # Merge adjacent segments for the same PID or consecutive idle periods
        if self.segments and self.segments[-1].pid == pid and self.segments[-1].end_time == start_time:
            self.segments[-1].end_time = end_time
        else:
            self.segments.append(GanttSegment(start_time, end_time, pid))

    def get_execution_order(self) -> List[str]:
        """Returns the sequential order of scheduled process execution."""
        return [seg.pid for seg in self.segments]

    def get_idle_intervals(self) -> List[Tuple[int, int, int]]:
        """Returns list of tuples: (idle_start, idle_end, duration)."""
        return [(seg.start_time, seg.end_time, seg.duration) for seg in self.segments if seg.is_idle]

    def render(self) -> str:
        """
        Renders a clean ASCII Gantt chart with aligned process labels
        and chronological timeline timestamps below.
        """
        if not self.segments:
            return "(Empty Gantt Timeline)"

        top_border = "+"
        content_line = "|"
        bot_border = "+"
        timeline_line = ""

        # Build chart blocks
        time_positions = [self.segments[0].start_time]

        for seg in self.segments:
            # Dynamic block width based on PID label length and segment duration
            label = seg.pid
            width = max(len(label) + 2, 6)
            
            top_border += "-" * width + "+"
            content_line += label.center(width) + "|"
            bot_border += "-" * width + "+"
            time_positions.append(seg.end_time)

        # Build timeline string with proper spacing
        timeline_tokens = [str(time_positions[0])]
        curr_idx = 0
        
        for i, seg in enumerate(self.segments):
            label = seg.pid
            width = max(len(label) + 2, 6)
            next_time_str = str(time_positions[i + 1])
            
            # Pad between previous timestamp and current timestamp
            space_needed = width + 1 - len(next_time_str)
            if space_needed > 0:
                timeline_line += " " * space_needed + next_time_str
            else:
                timeline_line += " " + next_time_str

        # Prepend initial start time
        timeline_line = str(time_positions[0]) + timeline_line[len(str(time_positions[0])):]

        chart_output = [
            top_border,
            content_line,
            bot_border,
            timeline_line
        ]
        return "\n".join(chart_output)
