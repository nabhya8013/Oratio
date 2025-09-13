package models

type Session struct {
    AudioPath      string
    StartTime      string
    Transcription  string
    PitchMean      float64
    PitchStd       float64
    RMSMean        float64
    RMSStd         float64
    EmotionLabel   string
    EmotionScore   float64
    SimilarityScore float64
}

type VADResult struct {
    StartTime    string `json:"start_time"`
    Transcription string `json:"transcription"`
}

type FeatureResult struct {
    PitchMean float64 `json:"pitch_mean"`
    PitchStd  float64 `json:"pitch_std"`
    RMSMean   float64 `json:"rms_mean"`
    RMSStd    float64 `json:"rms_std"`
}

type SERResult struct {
    Label string  `json:"label"`
    Score float64 `json:"score"`
}

type SimilarityResult struct {
    Similarity float64 `json:"similarity"`
}
