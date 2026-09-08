using Xunit;
using Qase.Csharp.Commons.Attributes;

namespace QaseXUnitShowcase;

[Suites("Unit", "Calculator")]
public class CalculatorTests
{
    [Theory]
    [InlineData(2, 3, 5)]
    [InlineData(10, 20, 30)]
    [InlineData(-5, 5, 0)]
    [QaseIds(300)]
    [Title("Addition returns the correct sum")]
    public void AdditionTest(int a, int b, int expected)
    {
        int result = a + b;
        Assert.Equal(expected, result);
    }
}
