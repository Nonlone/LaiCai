package stock

import "testing"

func TestFetchShareDividend(t *testing.T) {

	result := fetchShareDividend(&stock{
		Code: "601318",
		Name: "中国平安",
	})

	if len(result) == 0 {
		t.Error("result is empty")
		t.FailNow()
	}

}

func TestSyncShareDividend(t *testing.T) {

	result := fetchShareDividend(&stock{
		Code: "601318",
		Name: "中国平安",
	})

	if len(result) == 0 {
		t.Error("result is empty")
		t.FailNow()
	}

	err := syncShareDividend(result)
	if err != nil {
		t.Error(err)
		t.FailNow()
	}
}

func TestCalToShareDividendSat(t *testing.T) {

	sds := fetchShareDividend(&stock{
		Code: "601318",
		Name: "中国平安",
	})
	if len(sds) == 0 {
		t.Error("sds is empty")
		t.FailNow()
	}

	sdss := calToShareDividendSat(sds)
	if len(sdss) == 0 {
		t.Error("sdss is empty")
		t.FailNow()
	}
}


func TestSyncShareDividendSat(t *testing.T) { 

	sds := fetchShareDividend(&stock{
		Code: "601318",
		Name: "中国平安",
	})
	if len(sds) == 0 {
		t.Error("sds is empty")
		t.FailNow()
	}

	sdss := calToShareDividendSat(sds)
	if len(sdss) == 0 {
		t.Error("sdss is empty")
		t.FailNow()
	}

	err := syncShareDividendSat(sdss)
	if err != nil {
		t.Error(err)
		t.FailNow()
	}

	sdsl := calToShareDividendSatLatest(sdss)
	if sdsl == nil {
		t.Error("sdsl is nil")
		t.FailNow()
	}
	
	err = syncShareDividendSatLatest(sdsl)
}
