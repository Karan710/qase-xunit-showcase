using Xunit;

namespace QaseXUnitShowcase;

public class CalculatorTests
{
    [Theory]
    [InlineData(2, 3, 5)]
    [InlineData(10, 20, 30)]
    [InlineData(-5, 5, 0)]
    public void AdditionTest(int a, int b, int expected)
    {
        int result = a + b;
        Assert.Equal(expected, result);
    }
}
