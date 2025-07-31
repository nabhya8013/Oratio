package models

import (
	"time"

	"gorm.io/datatypes"
)

type Session struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	Speech      string         `json:"speech"`
	Questions   datatypes.JSON `json:"questions"` // store JSON array
	CreatedBy   string         `json:"created_by"`
	GeneratedBy string         `json:"generated_by"`
	CreatedAt   time.Time      `json:"created_at"`
}

type Question struct {
	NPCID int    `json:"npc_id"`
	Text  string `json:"text"`
}
