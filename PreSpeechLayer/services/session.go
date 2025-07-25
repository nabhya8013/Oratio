package services

// InsertSession inserts a new Session record into the database
import (
	"Oratio/models"
	"log"
	"time"

	"github.com/google/uuid"
)

func InsertSession(paper string, speech string, questions []models.Question) (string, error) {
	session := &models.Session{
		ID:         uuid.New().String(),
		Title:      paper,
		SpeechText: speech,
		CreatedAt:  time.Now(),
		Questions:  questions, // only if you added it to the model
	}

	if err := DB.Create(session).Error; err != nil {
		return "", err
	}

	return session.ID, nil
}

// GetSession fetches a session by ID
func GetSession(sessionID string) (*models.Session, error) {
	var session models.Session
	result := DB.First(&session, "id = ?", sessionID)
	if result.Error != nil {
		log.Printf("❌ Error fetching session %s: %v", sessionID, result.Error)
		return nil, result.Error
	}
	return &session, nil
}
