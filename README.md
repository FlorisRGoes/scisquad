
# SciSquad
This is a Python package developed by SciSports for the purpose of Squad Management. Please refer 
to the *Squad Management* section for more detailed information like the problem statement, use-cases and applications.

## Basic Usage

To use the functionality of this package, one needs to have a valid API client for the SciSports Recruitment Center
platform. Please contact `support@scisports.com` for more information if you do not already have an account, or you
don't have a valid API client. Note that accounts & API access are part of commercial subscriptions to SciSports
products, and costs might apply.

For the package to work, please clone the repository and make sure your local environment has a .env file with the
following variables:

* API_USER
* API_PW
* API_CLIENT_ID
* API_CLIENT_SECRET
* SCISPORTS_USER_ID
* SCISPORTS_ACCOUNT

Additionally, if you want to use custom explanations using the functionality in the `explanations` module, you need
to have an Azure Open-AI subscription, and need to include the following variables in your .env file:

* LLM_KEY
* LLM_ENDPOINT
* LLM_MODEL

## Squad Management

> ### Relevance of Squad Management in Modern-Day Football
> Johan Cruijff once said football is a simple game: “It is about always scoring one more goal than your opponent”. 
> And while this hasn’t changed since the beginning of the sport, the domain of professional football 
> has developed significantly over the last decades, 
> and has seen drastic changes in the way clubs are operated because of it. 
> In the past 30 years, we have seen a 10-20 fold increase in the annual amount of money spend on the football transfer 
> market, with the total market size expecting to grow to over €10B.
>
> Meanwhile, improved broadcast coverage and availability of data have significantly changed the way clubs scout for 
> new players. Whereas scouting could traditionally be imagined as the expert observer standing on the side-line spotting 
> talents based on experience, modern day scouts probably spend more time behind their desks than next to the field, 
> as scouting revolves around video & data-analysis, and has become more global than ever. 
> Finally, technological advancements like wide availability of cloud applications and easy access to AI-driven scouting 
> tools have resulted in the scouting game changing even further and becoming ever more digital. 
>
> The rapidly growing transfer market and substantial changes in the ways clubs scout for players signal the wider change 
> in the way football clubs are operated. Modern day operations involve higher stakes (large amounts of money) and require 
> vastly different skills compared to 30 years ago. This has recently been accelerated by the increasing availability of 
> new AI- and data-driven technologies, that also come with changing operational requirements due to 
> new legal frameworks like the EU GDPR and AI Act legislation. When all taken together, it signals the relevance of 
> trustworthy state-of-the art data-driven solutions for squad management, to algin with the needs of a modern-day 
> scouting department.  

### Use-case Definition
For the purpose of the squad management use-case we assume the main goal of a professional team is two-fold: 
(1) to win games and (2) to sell players for a profit. To achieve this, one needs to be able to evaluate the current 
state of the team, and to plan for the coming 6-12 months ahead, in order to be able to optimize the squad 
towards the future to achieve these goals. In particular, squad management is about supporting optimial decision-making 
in the following areas: (1) contract extensions, (2) buying and selling players and (3) minute distribution across the
team.

As such, the SciSquad packages provides a set of functionalities that can be used to support the following tasks, 
typically conducted in this order to evaluate and optimize a team's squad:

1. Retrieve all team information, like fixtures in the various competitions, the current roster, development of the team etc. 
2. Benchmark the team against other teams in the same league, using the main (domestic) league a team participates in.
3. Analyze the team's strong and weak spots using the league benchmarks.
4. Analyze the state of current squad, and generate alerts for the user to act upon.
5. Automatically generate a scouting plan for the squad, that acts on the weak spots and alerts found.
6. Execute a guided-player search based on the scouting plan, accounting for club preferences and budget constraints that are automatically generated from past data.
7. Simulate the impact of adding new players to the squad, both in terms of changes in team performance as well as the impact on the individual performance and ETV development of other players on the team.

### Demos

Dashboard examples and jupyter notebooks with example workflows are available in the `demos` folder.

## Acknowledgement
The demonstrators featured in this project are connected to the contributions of SciSports to 
the [TUPLES Trustworthy AI Project](https://www.tuples.ai). This project has received funding from the 
European Union’s HORIZON-CL4-2021-HUMAN-01 research and innovation programme under grant agreement No. 101070149

## 📜 Notice

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** 
license.

- ✅ You’re welcome to use, modify, and share this project for **personal, academic, or research purposes**.  
- ❌ **Commercial use is not allowed** — that means you can’t use this project (or parts of it) in products, services, 
- or activities that are intended for profit.  
- ℹ️ Full license details: [CC BY-NC 4.0 Legal Code](https://creativecommons.org/licenses/by-nc/4.0/legalcode)  

If you’d like to use this project in a commercial setting, please reach out to `support@scisports.com`r to discuss 
licensing options.  
