package stock

import (
	"testing"
)

func TestFetchBaicInfo(t *testing.T) {
	
	result := fetchBasicInfo()

	if len(result) == 0 {
		t.Error("result is empty")
		t.FailNow()
	} 

}

func TestSyncBasicInfo(t *testing.T) {


	result := fetchBasicInfo()

	if len(result) == 0 {
		t.Error("result is empty")
		t.FailNow()
	}

	err := syncBasicInfo(result)
	if err!=nil {
		t.Errorf("syncBasicInfo error: %v", err)
		t.FailNow()
	}


}