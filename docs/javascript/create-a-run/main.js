fetch('https://www.tofupilot.app/api/v1/runs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.TOFUPILOT_API_KEY}`,
  },
  body: JSON.stringify({
    procedure_id: 'FVT1',
    unit_under_test: {
      serial_number: 'PCBA01-0001',
      part_number: 'PCB01',
    },
    run_passed: true,
    duration: 'PT27M15S',
  }),
})
