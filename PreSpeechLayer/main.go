package main

import (
	"Oratio/routes"
	"Oratio/services"

	"github.com/gin-gonic/gin"
)

func main() {
	// Initialize Supabase DB connection
	services.InitDatabase()

	r := gin.Default()
	routes.RegisterRoutes(r)

	r.Run(":8080")
}
