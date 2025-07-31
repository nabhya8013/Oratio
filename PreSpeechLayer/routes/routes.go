package routes

import (
	"Oratio/handlers"

	"github.com/gin-gonic/gin"
)

func RegisterRoutes(r *gin.Engine) {
	r.POST("/generate", handlers.GenerateAndStore)
	r.GET("/session", handlers.GetSessionByQuery) // GET /session?id=2
}
