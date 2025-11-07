package services

import (
	"encoding/json"

	"Oratio/PreSpeechLayer/models"
)

func SaveSession(speech string, questions []models.Question) (*models.Session, error) {
	qbytes, err := json.Marshal(questions)
	if err != nil {
		return nil, err
	}

	session := models.Session{
		Speech:    speech,
		Questions: qbytes,
	}

	if err := DB.Create(&session).Error; err != nil {
		return nil, err
	}
	return &session, nil
}

func GetSessionByID(id uint) (models.Session, error) {
	var session models.Session
	err := DB.First(&session, id).Error
	return session, err
}
