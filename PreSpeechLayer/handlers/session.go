package handlers

import (
	"net/http"

	"Oratio/services"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

func GetSessionHandler(c *gin.Context) {
	idStr := c.Param("id")
	id, err := uuid.Parse(idStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid session ID"})
		return
	}

	session, err := services.GetSession(id.String()) // ✅ convert UUID to string
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Session not found"})
		return
	}

	c.JSON(http.StatusOK, session)
}

func GenerateHandler(c *gin.Context) {
	paper := c.PostForm("paper")
	result, err := services.Gemini(paper) // Call the Gemini service function
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate content"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"result": result})
}
