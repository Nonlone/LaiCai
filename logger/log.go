package logger

import (
	"log/slog"
	"os"
)

type Log interface { 
	Debug(msg string, args ...any)
	Info(msg string, args ...any)
	Warn(msg string, args ...any)
	Error(msg string, args ...any)
	Fatal(msg string, args ...any)
}

type logAdapter struct {
	Log

	s *slog.Logger
}

func (l *logAdapter) Debug(msg string, args ...any) {
	l.s.Debug(msg, args...)
}

func (l *logAdapter) Info(msg string, args ...any) {
	l.s.Info(msg, args...)
}

func (l *logAdapter) Warn(msg string, args ...any) {
	l.s.Warn(msg, args...)
}

func (l *logAdapter) Error(msg string, args ...any) {
	l.s.Error(msg, args...)
}

func (l *logAdapter) Fatal(msg string, args ...any) {
	l.s.Error(msg, args...)
}



func New() Log {
	return &logAdapter{
		s: slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{
			Level: slog.LevelDebug,
		})),
	}
}