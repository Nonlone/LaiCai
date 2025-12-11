package db

import (
	"LaiCai/logger"
	"database/sql"
	"time"

	 _ "github.com/go-sql-driver/mysql"
)


const (
	dsn = "root:123456@tcp(127.0.0.1:3306)/LaiCai?charset=utf8mb4&parseTime=True&loc=Local"
)

func RawConn() *sql.DB {
	logger := logger.New()

	db,err := sql.Open("mysql",dsn)
	if  err!=nil {
		panic(err)
	}

	go func() {
		defer func(){
			r := recover()
			if r != nil {
				logger.Error("db.RawConn panic: %v", r)
			}
		}()

		ticker := time.NewTicker(time.Minute * 5)

		for range ticker.C {
			err := db.Ping()
			if err != nil {
				logger.Error("db.RawConn Ping error: %v", err)
			}
		}	
	}()

	return db
}