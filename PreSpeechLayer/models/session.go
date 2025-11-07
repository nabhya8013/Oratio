package models

import (
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

type Session struct {
	gorm.Model
	Speech         string         `json:"speech"`
	Questions      datatypes.JSON `json:"questions"`
	Transcript     string         `json:"transcript,omitempty" gorm:"type:text"`
	AnalysisResult datatypes.JSON `json:"analysis_result,omitempty" gorm:"type:jsonb"`
	AudioBucket    string         `json:"audio_bucket,omitempty"`
	AudioPath      string         `json:"audio_path,omitempty"`
}

type Question struct {
	gorm.Model
	SessionID uint   `json:"session_id"`
	Text      string `json:"text"`
	NpcID     int    `json:"npc_id"`
}
