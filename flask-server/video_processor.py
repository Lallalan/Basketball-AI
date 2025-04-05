import supervision as sv
from tqdm import tqdm
from player_tracking import PlayerTracker

class VideoProcessor:
    def __init__(self, api_key):
        self.player_tracker = PlayerTracker(api_key)
    
    def process_video(self, input_path, output_path):
        # Get video info
        video_info = sv.VideoInfo.from_video_path(input_path)
        
        # Initialize video writer
        with sv.VideoSink(output_path, video_info) as sink:
            # Process each frame
            for frame in tqdm(
                sv.get_video_frames_generator(input_path), 
                total=video_info.total_frames,
                desc="Processing video"
            ):
                # Track players
                detections = self.player_tracker.process_frame(frame)
                
                # Annotate frame
                annotated_frame = self.player_tracker.annotate_frame(frame, detections)
                
                # Write frame
                sink.write_frame(annotated_frame)
        
        return True