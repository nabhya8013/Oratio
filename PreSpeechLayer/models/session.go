package models

import "time"

type Session struct {
	ID          string     `gorm:"primaryKey" json:"id"`
	CreatedAt   time.Time  `json:"created_at"`
	Title       string     `json:"title"`
	GeneratedBy string     `json:"generated_by"`
	SpeechText  string     `json:"speech_text"`
	Questions   []Question `gorm:"-" json:"questions"` // Ignored by GORM unless you want to model a relation
}

type GeminiResponse struct {
	SessionID string      `json:"session_id"`
	Speech    string      `json:"speech"`
	Questions []NPCPrompt `json:"questions"`
}

type NPCPrompt struct {
	NPCID int    `json:"npc_id"`
	Text  string `json:"text"`
}

type Question struct {
	NPCID int    `json:"npc_id"`
	Text  string `json:"text"`
}
