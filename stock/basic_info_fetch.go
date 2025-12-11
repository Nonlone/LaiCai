package stock

import (
	"LaiCai/logger"
	"encoding/json"

	"github.com/go-resty/resty/v2"
)

func fetchBasicInfo() []*BasicInfo {
	log := logger.New()

	client := resty.New()

	resp, err := client.R().Get(aktoolsPrefix + "/stock_info_a_code_name")
	if err != nil {
		log.Error("fetchBasicInfo error: %v", err)
		return nil
	}

	if resp.IsSuccess() {

		type temp struct {
			Code string `json:"code"`
			Name string `json:"name"`
		}

		var ts []*temp
		err := json.Unmarshal(resp.Body(), &ts)
		if err != nil {
			log.Error("fetchBasicInfo json.Unmarshal error: %v", err)
			return nil
		}
		
		result := make([]*BasicInfo, 0, len(ts))
		for _, v := range ts {
			result = append(result, NewBasicInfo(v.Code, v.Name))
		}
		return result
	}

	return nil
}
