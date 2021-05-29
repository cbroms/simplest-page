const express = require("express");
const proxy = require("express-http-proxy");
const app = express();
const port = 5000;

const dotenv = require("dotenv");

dotenv.config();

app.use(
  "/",
  proxy("https://cdn.simplest.page", {
    proxyReqPathResolver: (req) => {
      return new Promise(function (resolve, reject) {
        setTimeout(() => {
          // simulate async
          let resolvedPathValue = "";
          const hasEnd = req.url.includes(".");
          const cleanUrl =
            req.url[req.url.length - 1] === "/"
              ? req.url.substr(0, req.url.length - 1)
              : req.url;
          if (!hasEnd) resolvedPathValue = cleanUrl + "/index.html";

          resolvedPathValue = process.env.URL_REWRITE + resolvedPathValue;
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
