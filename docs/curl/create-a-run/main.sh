curl -X POST https://www.tofupilot.app/api/v1/runs -H "Content-Type: application/json" -H "Authorization: Bearer ${TOFUPILOT_API_KEY}" -d '{
    "procedure_id": "FVT1",
    "unit_under_test": {
      "serial_number": "PCBA01-0001",
      "part_number": "PCB01"
    },
    "run_passed": true,
    "duration": "PT27M15S"
}'