const express = require("express");
const proxy = require("express-http-proxy");
const redis = require("async-redis");
const Handlebars = require("handlebars");
global.Handlebars = Handlebars;
const app = express();
const port = 5000;

const dotenv = require("dotenv");

dotenv.config();

require("./templates/settings.precompiled.js");
require("./templates/error.precompiled.js");

const redisClient = redis.createClient({ host: "redis" });

app.get("/settings/session/:id", async (req, res) => {
  try {
    // check that the id provided is valid
    const blogInfo = JSON.parse(await redisClient.get(req.params.id));

    if (blogInfo === undefined || blogInfo === null) {
      // session no longer exists, 404 it
      const errorTemplate = Handlebars.templates.error;
      const html = errorTemplate({
        errorCode: 404,
        errorMessage: "Couldn't find that page.",
      });
      res.statusCode(404).send(html);
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
      const settingsTemplate = Handlebars.templates.settings;
      const html = settingsTemplate(blogInfo);

      res.send(html);
    }
  } catch (e) {
    console.log(e);
    // in the event of an error, return a default 500 response
    const errorTemplate = Handlebars.templates.error;
    const html = errorTemplate({
      errorCode: 500,
      errorMessage:
        "Something went wrong. Try again in a bit, or <a href='mailto:human@simplest.page'>contact me</a> if this issue persists.",
    });
    res.statusCode(500).send(html);
  }
});

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
  proxy(process.env.CDN_DOMAIN, {
    proxyReqPathResolver: (req) => {
      return new Promise((resolve, reject) => {
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
          sitename = "assorted";
          const parts = req.get("host").split(".");
          if (parts.length > 2) sitename = parts[0];

          resolvedPathValue =
            process.env.URL_REWRITE + sitename + resolvedPathValue;
          console.log(resolvedPathValue);
          resolve(resolvedPathValue);
        }, 200);
      });
    },
    userResDecorator: (proxyRes, proxyResData, userReq, userRes) => {
      // quick and dirty check for if the page doesn't exist or isn't accessible
      if (proxyRes.statusCode === 404 || proxyRes.statusCode === 403) {
        const errorTemplate = Handlebars.templates.error;
        const html = errorTemplate({
          errorCode: 404,
          errorMessage: "Couldn't find that page.",
        });
        // the ability to mutate response headers supposedly will be removed in the future
        // https://www.npmjs.com/package/express-http-proxy#exploiting-references
        userRes.setHeader("Content-Type", "text/html");
        return html;
      } else {
        return proxyResData;
      }
    },
  })
);

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
