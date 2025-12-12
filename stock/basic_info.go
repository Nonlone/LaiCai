package stock

import "time"

type marketType string

const (
	Unknown marketType = "Unknown"
	SH      marketType = "SH"
	SZ      marketType = "SZ"
)

type stock struct {
	Code string `json:"code" db:"code"`
	Name string `json:"name" db:"name"`
}

func (s *stock) Market() marketType {
	if s.Code[0] == '6' {
		return SH
	} else if s.Code[0] == '0' || s.Code[0] == '3' {
		return SZ
	}
	return Unknown

}

type BasicInfo struct {
	stock
	Market marketType `json:"market" db:"market"`
	audit
}

func NewBasicInfo(code string, name string) *BasicInfo {
	now := time.Now()
	s := &stock{
		Code: code,
		Name: name,
	}
	result := &BasicInfo{
		stock:  *s,
		Market: s.Market(),
		audit: audit{
			CreatedAt: now,
			UpdatedAt: now,
		},
	}

	return result
}
