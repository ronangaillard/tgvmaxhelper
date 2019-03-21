const request = require('request');
const fs = require('fs');
const opn = require('opn');

travelData = [];

function getUrl(city_from, city_to)
{
    city_from.replace(/ /g, "+");
    city_to.replace(/ /g, "+");
    return "https://data.sncf.com/api/records/1.0/search/?dataset=tgvmax&facet=date&facet=origine&facet=destination&facet=od_happy_card&refine.origine=" + city_from + "&refine.destination=" + city_to + "&refine.od_happy_card=OUI";
}

function printInfo(travels, i)
{
    if (i >= travels.length) {
        fs.writeFile("front/data.js", "var travelData = " + JSON.stringify(travelData) + ";", function (err) {
            if (err) {
                return console.log(err);
            }

            console.log("The file was saved!");

            opn('./front/locales.html');
        }); 
        return;
    }
   
    var travel = travels[i];
    console.log("Looking for travel from " + travel.city_from + " to " + travel.city_to);
    request(getUrl(travel.city_from, travel.city_to), function (error, reponse, body) {
        if (body) {
            var result = JSON.parse(body);
            result.records.forEach(function (element) {
                travelData.push({
                    title: travel.city_from + " to " + travel.city_to,
                    start: element.fields.date + "T" + element.fields.heure_depart, 
                    end: element.fields.date + "T" + element.fields.heure_arrivee 
                });
                console.log(element.fields.date + " : " + element.fields.heure_depart + " -> " + element.fields.heure_arrivee);
            });
            printInfo(travels, ++i);
        }
    });
}

fs.readFile('config.json', 'utf8', function(err, contents) {
    travels = JSON.parse(contents);
   
    printInfo(travels.travels, 0);
});

