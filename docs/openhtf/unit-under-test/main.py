  from openhtf import Test
  from tofupilot.openhtf import TofuPilot

  def main():
      phases = [ ] # Your test phases here
      test = Test(phases,
          part_number = "PCB1",
          revision = "A",           # optional
          batch_number = "12-24",   # optional
      )
      with TofuPilot(test):
          test.execute(lambda: 'PCB1A001') # UUT S/N

  if __name__ == '__main__':
      main()
