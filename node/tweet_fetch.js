const { Rettiwt } = require('rettiwt-api');
const fs = require('fs');
const path = require('path');
const franc = require('franc');

// store all available api keys here
const apiKeys = ["a2R0PUNrZFJxMmJFNXl1REFLbHJxS0p4d0NZY0U3aHVLc2JLT2VRbUphOVY7YXV0aF90b2tlbj03ZjhlYzBlZGFhZWNiZjZlMWNkMjIwYjM0ZDBlZDY0YTU2MzkxM2U5O2N0MD1mYTg3OWI0YTI1OTk1N2MxYTYyZjFjYTI1ODkxOWVjOWZlZjEzOGQ2YTZmMTgzMDMwNjczMDFkY2UwOTkyZDlkNWFmNWRkZmFkZWM4NDVjNTI5YTc1Y2VlOTg4ZDZkOGRmYjk0OWFiZTE0Nzg3MzRkMTIzMjUwNmM0Yjg5MGVlMGNjZjkxYzc5MTcyYzI5NmM3MzA0NDM4MDRhMjViYmY0O3R3aWQ9dSUzRDE2NzE0MzAzMDg4NzE0MDU1Njg7"];

function createRandomRettiwt() {
    const randomKey = apiKeys[Math.floor(Math.random() * apiKeys.length)];
    return new Rettiwt({
        apiKey: randomKey,
        logging: false, // set to false for cleaner output
        delay: () => 1000 + Math.random() * 500
    });
}

async function fetchTweets(topic, totalCount) {
    try {
        console.log(`🚀 starting fetch for '${topic}'...`);
        const outputPath = path.join(__dirname, '..', 'tweets.json');
        
        const allTweets = [];
        const seenTexts = new Set();
        
        // clean hashtag
        const hashtag = topic.replace(/\s+/g, '').replace('#', '');

        const filters = [
            { keywords: [topic] },
            { hashtags: [hashtag] }
        ];

        let consecutiveErrors = 0;
        const maxErrors = 5;

        for (const filter of filters) {
            // If we already have enough, don't start a new filter
            if (allTweets.length >= totalCount) break;

            while (allTweets.length < totalCount) {
                if (consecutiveErrors >= maxErrors) break;

                const remaining = totalCount - allTweets.length;
                // Fetch a bit more than remaining because of language filtering
                const fetchSize = Math.min(40, Math.max(10, remaining * 2));

                const rettiwt = createRandomRettiwt();

                try {
                    const result = await rettiwt.tweet.search({
                        ...filter,
                        maxResults: fetchSize
                    });
                    
                    if (!result || !result.list || result.list.length === 0) break;

                    for (const tweet of result.list) {
                        const text = tweet.fullText || '';
                        
                        // Reliability: Use API lang if available, fallback to franc for safety
                        const isEnglish = (tweet.lang === 'en') || (text.length > 20 && franc(text) === 'eng');
                        
                        if (isEnglish && !seenTexts.has(text) && allTweets.length < totalCount) {
                            allTweets.push({ text: text });
                            seenTexts.add(text);
                        }
                    }

                    console.log(`🔁 fetched ${allTweets.length}/${totalCount} english tweets so far...`);
                    consecutiveErrors = 0;
                    
                    if (allTweets.length >= totalCount) break;

                    await new Promise(r => setTimeout(r, 500));

                } catch (err) {
                    consecutiveErrors++;
                    console.error(`⚠️ api error: ${err.message}`);
                    await new Promise(r => setTimeout(r, 1000));
                    continue;
                }
            }
        }

        if (allTweets.length > 0) {
            fs.writeFileSync(outputPath, JSON.stringify({
                success: true,
                tweets: allTweets // No need to slice, we checked count during pushing
            }, null, 2));

            console.log(`✅ successfully fetched ${allTweets.length} english tweets`);
        } else {
            console.error('❌ no english tweets found');
            process.exit(1);
        }

    } catch (error) {
        console.error('❌ critical error:', error.message);
        process.exit(1);
    }
}

// Logic to correctly parse topic and count from arguments
const args = process.argv.slice(2);
let topicArg, countArg;

if (args.length >= 2) {
    // If last arg is a number, assume it's the count
    if (!isNaN(args[args.length - 1])) {
        countArg = parseInt(args.pop());
        topicArg = args.join(' ');
    } else {
        topicArg = args.join(' ');
        countArg = 20;
    }
} else {
    topicArg = args[0];
    countArg = 20;
}

if (topicArg) {
    fetchTweets(topicArg, countArg);
} else {
    console.error('❌ topic is required');
    process.exit(1);
}
