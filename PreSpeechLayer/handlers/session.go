package handlers

import (
	"net/http"

	"Oratio/models"
	"Oratio/services"
	"encoding/json"

	"github.com/gin-gonic/gin"
)

func GenerateHandler(c *gin.Context) {
	paper := c.PostForm("paper")
	result, err := services.Gemini(paper) // Call the Gemini service function
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate content"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": result})
}

func GenerateAndStore(c *gin.Context) {
	paper := c.PostForm("paper")

	result, err := services.Gemini(paper)
	if err != nil {
		c.JSON(500, gin.H{"error": "Gemini failed"})
		return
	}

	var questions []models.Question
	if err := json.Unmarshal(result.Questions, &questions); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse questions"})
		return
	}

	session, err := services.SaveSession(result.Speech, questions)
	if err != nil {
		c.JSON(500, gin.H{"error": "DB insert failed"})
		return
	}

	c.JSON(200, session)
}
