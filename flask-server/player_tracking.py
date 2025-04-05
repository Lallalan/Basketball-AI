from inference import get_roboflow_model
import supervision as sv
import numpy as np
import os

class PlayerTracker:
    def __init__(self, api_key, model_id="basketball-players-2-qwvnh/3", player_id=4, max_players=10, tracking_buffer=30):
        self.PLAYER_ID = player_id
        self.MAX_PLAYERS = max_players
        self.TRACKING_BUFFER = tracking_buffer
        
        # Initialize models
        self.PLAYER_DETECTION_MODEL = get_roboflow_model(model_id=model_id, api_key=api_key)
        self.tracker = sv.ByteTrack()
        self.tracker.reset()
        
        # Initialize annotators
        self.ellipse_annotator = sv.EllipseAnnotator(thickness=3)
        self.label_annotator = sv.LabelAnnotator(text_position=sv.Position.BOTTOM_CENTER)
        
        # Tracking state
        self.lost_players = {}
        self.previous_tracker_ids = set()
    
    def process_frame(self, frame):
        # Perform detection
        result = self.PLAYER_DETECTION_MODEL.infer(frame, confidence=0.3)[0]
        detections = sv.Detections.from_inference(result)
        
        # Filter basketball players
        all_detections = detections[detections.class_id == self.PLAYER_ID]
        all_detections = all_detections.with_nms(threshold=0.3, class_agnostic=True)
        all_detections.class_id -= 1
        
        # Sort and limit detections
        if len(all_detections.confidence) > 0:
            sorted_indices = sorted(
                range(len(all_detections.confidence)),
                key=lambda i: all_detections.confidence[i],
                reverse=True
            )[:self.MAX_PLAYERS]
            
            all_detections = sv.Detections(
                xyxy=np.array([all_detections.xyxy[i] for i in sorted_indices]),
                confidence=np.array([all_detections.confidence[i] for i in sorted_indices]),
                class_id=np.array([all_detections.class_id[i] for i in sorted_indices])
            )
        
        # Update tracker
        tracked_detections = self.tracker.update_with_detections(detections=all_detections)
        
        # Track lost players
        active_tracker_ids = set(tracked_detections.tracker_id)
        lost_now = self.previous_tracker_ids - active_tracker_ids
        
        # Update lost players tracking
        for lost_id in list(self.lost_players.keys()):
            self.lost_players[lost_id] -= 1
            if self.lost_players[lost_id] <= 0:
                del self.lost_players[lost_id]
        
        for lost_id in lost_now:
            if lost_id not in self.lost_players:
                self.lost_players[lost_id] = self.TRACKING_BUFFER
        
        # Remove recovered players
        for tracker_id in active_tracker_ids:
            self.lost_players.pop(tracker_id, None)
        
        self.previous_tracker_ids = active_tracker_ids.copy()
        
        return tracked_detections
    
    def annotate_frame(self, frame, detections):
        labels = [f"#{tracker_id}" for tracker_id in detections.tracker_id]
        annotated_frame = frame.copy()
        annotated_frame = self.ellipse_annotator.annotate(
            scene=annotated_frame, 
            detections=detections
        )
        annotated_frame = self.label_annotator.annotate(
            scene=annotated_frame,
            detections=detections,
            labels=labels
        )
        return annotated_frame
    
