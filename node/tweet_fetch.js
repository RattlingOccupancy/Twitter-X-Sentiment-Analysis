// import required modules
const { Rettiwt } = require('rettiwt-api');
const fs = require('fs');
const path = require('path');
const francModule = require('franc');
const franc = francModule.franc;

// store all available api keys here (add multiple for better rotation)
const apiKeys = [
    "api_keys"
];

// helper: create a rettiwt instance using a random api key and random delay
function createRandomRettiwt() {
    const randomKey = apiKeys[Math.floor(Math.random() * apiKeys.length)];
    return new Rettiwt({
        apiKey: randomKey,
        logging: true,
        delay: () => 1000 + Math.random() * 1000 // random delay between 1-2 sec
    });
}

// main function: fetch tweets based on topic and save them
async function fetchTweets(topic, totalCount) {
    try {
        // check if topic is provided
        if (!topic) {
            console.error('❌ topic is required as a command-line argument');
            process.exit(1);
        }

        console.log(`🚀 starting fetch for '${topic}'...`);

        // set output file path for saving tweets
        const outputPath = path.join(__dirname, '..', 'tweets.json');
        const allTweets = [];

        // define search filters: both keywords and hashtags
        const filters = [
            { keywords: [topic] },
            { hashtags: [topic.replace('#', '')] }
        ];

        // loop through both filters and fetch tweets until required count is reached
        for (const filter of filters) {
            while (allTweets.length < totalCount) {
                const remaining = totalCount - allTweets.length;
                const batchSize = Math.min(50, remaining);

                // create a new rettiwt instance with random api key for every call
                const rettiwt = createRandomRettiwt();

                let tweets;
                try {
                    // fetch tweets based on current filter and batch size
                    tweets = await rettiwt.tweet.search({
                        ...filter,
                        maxResults: batchSize
                    });
                } catch (err) {
                    // handle api key errors and retry with another key
                    console.error(`⚠️ api key error (will try another on next call): ${err.message}`);
                    continue;
                }

                // stop fetching if no tweets are returned
                if (!tweets || !tweets.list || tweets.list.length === 0) break;

                // filter out english tweets only using 'franc' language detection
                const englishTweets = tweets.list.filter(t =>
                    (t.fullText || '').length > 20 && franc(t.fullText || '') === 'eng'
                );

                // store only tweet text
                allTweets.push(...englishTweets.map(t => ({ text: t.fullText })));

                console.log(`🔁 fetched ${allTweets.length}/${totalCount} english tweets so far...`);

                // add optional delay to avoid rate-limiting
                await new Promise(resolve => setTimeout(resolve, 500));
            }

            // stop if we have already fetched enough tweets
            if (allTweets.length >= totalCount) break;
        }

        // save tweets to file if any english tweets are found
        if (allTweets.length > 0) {
            fs.writeFileSync(outputPath, JSON.stringify({
                success: true,
                tweets: allTweets.slice(0, totalCount)
            }, null, 2));

            console.log(`✅ successfully fetched ${allTweets.length} english tweets`);
        } else {
            console.error('❌ no english tweets found');
            process.exit(1);
        }

    } catch (error) {
        // handle any unexpected errors
        console.error('❌ final error:', error.message);
        process.exit(1);
    }
}

// read topic from command-line arguments
const [topic] = process.argv.slice(2);
const count = 20;

// start fetching tweets
fetchTweets(topic, count);




























