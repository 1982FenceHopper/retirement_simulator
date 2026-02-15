# Retirement Simulator

> ### ***"Our favorite holding period is forever"***
> Warren Buffet

**Live Preview at https://monte-carlo-retirement-simulator.streamlit.app/**

Simulating retirement funds via Monte Carlo methods.

Calculates 5000 scenarios per year

### Features
- Current and Retirement Ages
- Annual Withdrawal (post-retirement) and Annual Deposit (pre-retirement)
- Market Crash at percentage and age
- Volatile Market Returns 3 years after crash (Dynamic Standard Deviation)
- Lowered Market Returns after retirement (Transfer of assets into bonds/cash for security)

### The Math
- $V = \text{Balance amount}$
- $a_{s} = \text{Current age (Starting age essentially)}$
- $a_{r} = \text{Retirement age}$
- $t = \text{Time step}$ (For example, 20 to 21 years is 1 time step, whilst 20 to 26 is 6 time steps)
- $r = \text{Return percentage for current year and current scenario}$
- $D = \text{Annual deposit amount}$
- $W = \text{Annual withdrawal amount}$
- $C = \text{Market crash percentage}$
- $a_{c} = \text{Market crash age}$
- $\sigma = \text{Standard Deviation (spread)}$


| Phase | Condition | Formula | Purpose |
| :---- | :-------: | :-----: | ------: |
|**Accumulation**|$(a_{s} + t) \; \lt \; a_{r}$|$V_{t} = V_{t-1} \cdot (1+\frac{r}{100}) + D$|Accumulate wealth before retirement|
|**Retirement**|$(a_{s} + t) \; \ge \; a_{r}$|$V_{t} = V_{t-1} \cdot (1+\frac{r}{100}) - W$|Use accumulated wealth to retire comfortably|
|**Market crash**|$(a_{s} + t) = a_{c}$|$V_{t} = V_{t} \cdot (1-\frac{C}{100})$|Simulate severe loss after a crash|
|**Crash aftermath**|$a_{c} \; \le \; (a_{s} + t) \; \le \; (a_{c} + 3)$|$\sigma = \sigma \cdot 1.5$|Simulate extreme volatility of a recovering market (3-year period)|

## Explanation
The Monte Carlo method here utilizes a simple Gaussian Distribution to get randomized multiplier values.

These random values represents the possible returns for the current year in the market. Because of the random walk nature (Brownian Motion<sup>[1](#footnotes)</sup>) of the financial market overall, it is almost taboo to think that each years percentage return **WILL ALWAYS** be the average return. As such, thousands of possible scenarios, each with a return that is slightly different than the average, but almost never the average itself, is used to pull up probabilities of the years possible return in the form of your savings account balance either going up or down by an indeterminate amount.

Say the average market return of the [$SPY](https://finance.yahoo.com/quote/SPY/) ETF (an example here), in the past 20 years, is ~5% [Hypothetical]. That is our mean value.

The [$SPY](https://finance.yahoo.com/quote/SPY/) will **NEVER** give **EXACTLY** 5% every year, due to the market following a random walk. As such, we use an algorithm utilizing a Gaussian Distribution to generate randomized return values that are deviated from the mean (called Standard Deviation or spread, which can be held as +/- 3% here).

We generate a 100,000 different possible return values, or scenarios. Think of each scenario being different realities. The [$SPY](https://finance.yahoo.com/quote/SPY/) in one reality could have returned 3.4%, whilst in another reality, within that SAME YEAR, it could have retured 7.5%. Every year, all 100,000 realities have different returns from the [$SPY](https://finance.yahoo.com/quote/SPY/).

This process, called a stochastic process, essentially allows us to make a probable guess as to the probability of the returns of one year, without assuming a definitive return value, by making use of random, independent numbers that if all were averaged, would converge down to the true mean, that is, the 5% average return. (Central Limit Theorem<sup>[3](#footnotes)</sup>)

Done for every year, coupled with deposits for every year until retirement, where withdrawal comes in, it could be used to determine how well different setups of the infamous "Buy-And-Hold<sup>[2](#footnotes)</sup>" strategy works for wealth investment.

The program also factors in one market crash, where on the year of the market crash, a portion of the account balance corresponding to the percentage crashed is taken out.

It also accommodates the fact that in the aftermath of an immediate crash, volatility skyrockets, as such the program modifies the standard deviation by a static amount (set to 1.5x here, which takes the +/- 3% stddev to +/- 4.5%. On a big account, that 1.5% extra spread can cause extreme losses or wins in some scenarios).

### Performance

As of right now, the only performance improvement this simulator makes is pre-calculating the 100,000 possible market returns for each year, for all the years.

**2D Tensor Mapping**: At first a 1D array was outputted, because the generation function was called per iteration of a loop. However, this time, the total number of years needed to simulate is calculated, then passed into the generation function to form a 2D vector. Axis 0 represents your year and Axis 1 represents all possibilities for the current year.

**Increased Cache Hit**: Pre-calculation allows usage of high-speed cache to avoid continuous calls to the RNG (Random Number Generator) to lower processing overhead.

**Parallelism**: This process mimics SIMD (Single Instruction, Multiple Data) execution. Albeit being run on CPU via NumPy's C-API, it can be quite easily ported to either GPGPU (e.g. CuPy) or FPGA (HLS) acceleration, where scenarios can be processed in parallel across hardware pipelines.

### Footnotes

1. A physics theory that details the random movement of particles due to inter-particle collision, which applies directly, and quite nicely, to the movement of the market - [Wikipedia](https://en.wikipedia.org/wiki/Brownian_motion)

2. An investment strategy where an investor buys a diverse portfolio of stocks, bonds, index funds and other financial assets, to then hold them for long term wealth gains, utilizing asset appreciation despite volatility setbacks - [Wikipedia](https://en.wikipedia.org/wiki/Buy_and_hold)

3. A part of probability theory, that dictates the fact that: Given a sufficiently large sample size from a population of finite level variance, the mean of all the samples from the same population will be approximately equal to the mean of the population, and the samples will follow a normal distribution (Gaussian) pattern, regardless of the population's actual distribution shape - [Wikipedia](https://en.wikipedia.org/wiki/Central_limit_theorem)

## License
```
This project is under the MIT license, view LICENSE for more details.
```