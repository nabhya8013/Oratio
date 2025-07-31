package handlers

import (
	"net/http"
	"strconv"

	"Oratio/models"
	"Oratio/services"
	"encoding/json"

	"github.com/gin-gonic/gin"
)

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

func GetSessionByQuery(c *gin.Context) {
	idStr := c.Query("id")
	if idStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'id' query parameter"})
		return
	}

	id, err := strconv.Atoi(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'id' parameter"})
		return
	}

	session, err := services.GetSessionByID(uint(id))
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	c.JSON(http.StatusOK, session)
}
