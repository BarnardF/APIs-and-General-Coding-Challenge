//I initially created this project using Python, to get a better understanding on how to structure the code/data

//The script uses script Properties for API keys — 
//reviewers will need to add their own NYT API key and TMDB Bearer token in project settings -
//script poperties (NYT_API_KEY and TMDB_TOKEN) to run the script

//GITHUB:
//https://github.com/BarnardF/APIs-and-General-Coding-Challenge/tree/main


//--------------Section A--------------------
function fetchNYTReviews(NYT_API_KEY, filterWord) {
  const url = `https://api.nytimes.com/svc/search/v2/articlesearch.json?&fq=typeOfMaterials%3AReview AND section.name%3AMovies&api-key=${NYT_API_KEY}`;
  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());


  const docs = data.response.docs;
  const filteredReviews = [];

  docs.forEach(movie => {
    const rawHeadline = movie.headline?.main || "N/A"; //https://javascript.plainenglish.io/why-optional-chaining-is-my-favorite-hidden-javascript-feature-27ddc809db46
    const cleanedHeadLine = rawHeadline.toLowerCase().trim();

    if (cleanedHeadLine.includes(filterWord)) {
      console.log(rawHeadline);

      const match = rawHeadline.match(/\u2018([^\u2019]+)\u2019/); //unicode for curly qoutes, claude assisted
      const movieTitle = match ? match[1].trim() : rawHeadline.split(':')[0].trim(); //claude assisted

      
      const newMovie = {
      headline: rawHeadline,
      movieTitle: movieTitle,
      abstract: movie?.abstract || "N/A",
      reviewAuthor: movie?.byline?.original || "N/A",
      articleID: movie?._id || "N/A",
      pubDate: movie?.pub_date || "N/A",
      reviewSource: movie?.source || "N/A",
      webUrl: movie?.web_url || "N/A"
      };
      filteredReviews.push(newMovie);
    }
  });

  //adding a row of data below the header
  //https://www.youtube.com/watch?v=6pugLx-ORU4
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const reviewSheet = ss.getSheetByName("NYT Reviews") || ss.insertSheet("NYT Reviews");
  reviewSheet.clearContents();

  const headers = ["headline", "movieTitle", "abstract", "reviewAuthor", "articleID", "pubDate", "reviewSource", "webUrl"];
  reviewSheet.getRange(1,1,1, headers.length).setValues([headers]);

  filteredReviews.forEach((review, index) => {
    const row = [
      review.headline,
      review.movieTitle,
      review.abstract,
      review.reviewAuthor,
      review.articleID,
      review.pubDate,
      review.reviewSource,
      review.webUrl
    ];
    reviewSheet.getRange(index + 2, 1, 1, row.length).setValues([row]) //caude assisted
  });

  if (filteredReviews.length == 0) {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const inputSheet = ss.getSheetByName("Dashboard");
    inputSheet.getRange("A2").setValue(`No reviews found for: "${filterWord}"`);
  }

  return filteredReviews
}



//--------------Section B--------------------
function fetchTMDBDetails(TMDB_TOKEN, filteredReviews) {
  const combinedResults = [];
  const options = {
    headers: {
      "accept": "application/json",
      "Authorization": `Bearer ${TMDB_TOKEN}`
    },
    muteHttpExceptions: true 
  };

  filteredReviews.forEach(movie => {
    const movieTitle = movie.movieTitle;
    const pubDate = movie.pubDate;
    const pubYear = pubDate.slice(0,4);
  
    //search for movie id
    const searchUrl = `https://api.themoviedb.org/3/search/movie?query=${encodeURIComponent(movieTitle)}&page=1`;
    const searchResponse = UrlFetchApp.fetch(searchUrl, options);
    const searchData = JSON.parse(searchResponse.getContentText());
    const results = searchData.results || [];

    if (results.length === 0) {
      console.log(`No TMDB match for: ${movieTitle}`);
      return;
    }

    //match by release year, or fall back to top result
    let movieID = null;
    for (const result of results) {
      if ((result.release_date || "").slice(0,4) === pubYear) {
        movieID = result.id;
        break;
      }
    }
    if (!movieID) movieID = results[0].id;

    const detailsUrl = `https://api.themoviedb.org/3/movie/${movieID}`;
    const detailResponse = UrlFetchApp.fetch(detailsUrl, options);
    const detailData = JSON.parse(detailResponse.getContentText());

    const tmdbFields = {
      tmdbId: detailData?.id || "N/A",
      tmdbTitle: detailData?.title || "N/A",
      originalTitle: detailData?.original_title || "N/A",
      releaseDate: detailData?.release_date || "N/A",
      budget: detailData?.budget || "N/A",
      revenue: detailData?.revenue || "N/A",
      popularity: detailData?.popularity || "N/A",
      voteAverage: detailData?.vote_average || "N/A",
      voteCount: detailData?.vote_count || "N/A",
      genres: (detailData.genres || []).map(g => g.name).join(", ") || "N/A",
      overview: detailData?.overview || "N/A",
      originCountry: (detailData.origin_country || []).join(", ") || "N/A",
      originalLanguage: detailData?.original_language || "N/A",
      homepage: detailData?.homepage || "N/A",
      tagline: detailData?.tagline || "N/A",
      };
      combinedResults.push(Object.assign({}, movie, tmdbFields));
      //console.log(combinedResults)

    console.log(`Matched '${movieTitle}' from TMDB ID: ${movieID}`);
  });

  //adding a row of data below the header
  //https://www.youtube.com/watch?v=6pugLx-ORU4
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const combinedSheet  = ss.getSheetByName("Combined Results") || ss.insertSheet("Combined Results");
  combinedSheet .clearContents();

  const headers = [
    "headline", "movieTitle", "abstract", "reviewAuthor", "articleID", "pubDate", "reviewSource", "webUrl", "tmdbId", "tmdbTitle", "originalTitle", "releaseDate", "budget", "revenue", "popularity", "voteAverage", "voteCount", "genres", "overview", "originCountry", "originalLanguage", "homepage", "tagline"
  ];
  combinedSheet.getRange(1, 1, 1, headers.length).setValues([headers]);

  combinedResults.forEach((result, index) => {
    const row = [
      result.headline, result.movieTitle, result.abstract, result.reviewAuthor, result.articleID, result.pubDate, result.reviewSource, result.webUrl, result.tmdbId, result.tmdbTitle, result.originalTitle, result.releaseDate, result.budget, result.revenue, result.popularity, result.voteAverage, result.voteCount, result.genres, result.overview, result.originCountry, result.originalLanguage, result.homepage, result.tagline
    ];
    combinedSheet.getRange(index + 2, 1, 1, row.length).setValues([row]);
  });

  return combinedResults;
}




function runAll() {
  // obtain api/token
  const scriptProperties = PropertiesService.getScriptProperties();
  const NYT_API_KEY = scriptProperties.getProperty('NYT_API_KEY');
  const TMDB_TOKEN = scriptProperties.getProperty('TMDB_TOKEN');

  if (!NYT_API_KEY || !TMDB_TOKEN) {
    console.log('API Key not found.');
    return;
  }
  console.log("Keys successfully loaded");


  //obtain filter word
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const inputSheet = ss.getSheetByName("Dashboard");
  const filterWord = inputSheet.getRange("B1").getValue().toString().toLowerCase().trim();

  if (!filterWord) {
    inputSheet.getRange("A2").setValue("Please enter a filter word");
    console.log("No filter word entered, type a keyword in B1");
    return;
  }
  console.log("filter word: " + filterWord);
  inputSheet.getRange("A2").setValue("");

  //filtered results
  const filteredReviews = fetchNYTReviews(NYT_API_KEY, filterWord);
  if (filteredReviews.length > 0) {
    inputSheet.getRange("A2").setValue(`${filteredReviews.length} review(s) found for: "${filterWord}"`)
  }
  //console.log(filteredReviews)

  // combined reults
  const combinedResults = fetchTMDBDetails(TMDB_TOKEN, filteredReviews);
}


