const express = require("express");
const proxy = require("express-http-proxy");
const redis = require("async-redis");
const Handlebars = require("handlebars");
global.Handlebars = Handlebars
const app = express();
const port = 5000;

const dotenv = require("dotenv");

dotenv.config();

require("./templates/settings.precompiled.js");

const redisClient = redis.createClient({ host: "redis" });

app.get('/settings/session/:id', async (req, res) => {
  try {
    // check that the id provided is valid 
    const blogInfo = JSON.parse(await redisClient.get(req.params.id))

    if (blogInfo === undefined || blogInfo === null) {
      // session no longer exists, 404 it
      res.sendStatus(404)
    } else {
      // we expect info to look like:
      /* 
      {
        subdomain: "theblogssubdomain",
        templates: {
          index: "the/path/to/the/index/template",
          page: "the/path/to/the/page/template",
        },
        author: "The Author <theauthors@email.com>"
      }
      */
      const settingsTemplate = Handlebars.templates.settings
      const html = settingsTemplate(blogInfo);

      res.send(html)
    }

  }
  catch (e) {
    console.log(e)
    // in the event of an error, return a default 500 response 
    res.sendStatus(500)
  }
})

// app.post('/settings/session/:id/update', (req, res) => {
//   try {
//     // check that the id provided is valid 
//     const retVal = redisClient.get(req.params.id)

//     if (retVal === undefined || retVal === null) {
//       // session no longer exists, 404 it
//       res.sendStatus(404)
//     }

//     // do something with the new data
//     // precompile the templates to check for errors and upload compiled versions 
//     // handlebars.precompile()


//   }
//   catch (e) {
//     res.sendStatus(500)
//   }
// })

app.use(
  "/",
  proxy("https://cdn.simplest.page", {
    proxyReqPathResolver: (req) => {
      return new Promise(function (resolve, reject) {
        setTimeout(() => {
          // simulate async
          let resolvedPathValue = "";
          const hasEnd = req.url.includes(".");
          // add .html to the end of the request if necessary 
          const cleanUrl =
            req.url[req.url.length - 1] === "/"
              ? req.url.substr(0, req.url.length - 1)
              : req.url;
          if (!hasEnd) resolvedPathValue = cleanUrl + "/index.html";

          // handle subdomains 
          sitename = 'assorted'
          const parts = req.get('host').split(".")
          if (parts.length > 2) sitename = parts[0]

          resolvedPathValue = process.env.URL_REWRITE + sitename + resolvedPathValue;
          console.log(resolvedPathValue);
          resolve(resolvedPathValue);
        }, 200);
      });
    },
  })
);

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
