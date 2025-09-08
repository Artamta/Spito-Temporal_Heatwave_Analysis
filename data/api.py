import cdsapi

dataset = "derived-era5-single-levels-daily-statistics"

for year in range(1979, 2019):
    request = {
        "product_type": "reanalysis",
        "variable": ["2m_temperature"],
        "year": str(year),
        "month": [
            "01", "02", "03", "04", "05", "06",
            "07", "08", "09", "10", "11", "12"
        ],
        "day": [
            "01", "02", "03", "04", "05", "06",
            "07", "08", "09", "10", "11", "12",
            "13", "14", "15", "16", "17", "18",
            "19", "20", "21", "22", "23", "24",
            "25", "26", "27", "28", "29", "30", "31"
        ],
        "daily_statistic": "daily_maximum",
        "time_zone": "utc+00:00",
        "frequency": "1_hourly",
        "area": [45, 35, -15, 135]
    }
    filename = f"era5_t2m_dailymax_{year}.nc"
    print(f"Downloading {filename} ...")
    client = cdsapi.Client()
    client.retrieve(dataset, request).download(filename)
