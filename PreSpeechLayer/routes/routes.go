package routes

import (
	"Oratio/handlers"

	"github.com/gin-gonic/gin"
)

func RegisterRoutes(r *gin.Engine) {
	r.POST("/generate", handlers.GenerateHandler)
	r.GET("/session/:id", handlers.GetSessionHandler)
}
