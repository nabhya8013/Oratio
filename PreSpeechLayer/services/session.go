package services

import (
	"Oratio/models"
	"encoding/json"
	"time"

	"gorm.io/datatypes"
)

func SaveSession(speech string, questions []models.Question) (*models.Session, error) {
	// Marshal []Question into JSON
	questionsJSON, err := json.Marshal(questions)
	if err != nil {
		return nil, err
	}

	session := models.Session{
		Speech:      speech,
		Questions:   datatypes.JSON(questionsJSON),
		GeneratedBy: "Gemini-2.5",
		CreatedAt:   time.Now(),
	}

	if err := DB.Create(&session).Error; err != nil {
		return nil, err
	}

	return &session, nil
}
