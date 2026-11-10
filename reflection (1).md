# Reflection: Fetching Public Car Part Data with Async Fetch

I built a web page that uses the Fetch API to asynchronously GET vehicle variable data from the NHTSA vPIC REST API. The script awaits the response, checks `response.ok`, parses the JSON, filters the `Results` array with a JSON object (`{ GroupName: "Active Safety System" }`), and displays the matches in a table. Loading and error messages keep the user informed while the request runs.

What surprised me most was that `fetch()` does not throw an error on HTTP failures like 404, so the status must be checked manually. I was also surprised that only 11 items matched, because related subgroups such as "Active Safety System/Lane and Side Assist" are excluded by an exact match.

My code evolved from a hard-coded URL to one built from a `queryParams` object using `URLSearchParams`, making the query easier to change. I also learned that JavaScript runs in the browser, not in the macOS Terminal.

I now better understand async/await, promises, and how a front end interoperates with a third-party service. I would like to learn more about CORS and how public APIs handle versioning.
