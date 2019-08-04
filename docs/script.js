'use strict'


// Create the map
let map;
function createMap(){

    //Create the map
    map = L.map( 'mapContainer', {
        center: [20.0, 5.0],
        minZoom: 2,
        zoom: 2,
        layers:[layerGroup]
    });

    //Add the base layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: ['a','b','c'],
        noWrap: true,
        bounds: [[-90, -180], [90, 180]],
        maxBoundsViscosity:1.0
    }).addTo(map);

}

var layerGroup = L.layerGroup([]);
function addMarker(lat, long, message, screen_name, id){
    var marker = L.marker([lat, long]).addTo(layerGroup);
    var tweet_url = "https://twitter.com/" + screen_name + "/status/" +id;
    marker.bindPopup(message + " -" + '<a href="'+tweet_url+'"target="_blank">'+screen_name+'</a>');
}

//# Form
function checkForm(){
    let term = document.forms["searchForm"]["searchBoxText"].value;
    
    if(isEmpty(term)){
        alert("Please Enter in term to search for.");
    }
    else{
        document.getElementById('submit').disabled = true;
        fetchData(term);
    }
}
function isEmpty(str){
    return !str.replace(/\s+/, '').length
}

//Fetch data
function fetchData(term){
    const base_url = 'https://qqs1tpf5pj.execute-api.eu-west-1.amazonaws.com/live/?term="';
    term = encodeURIComponent(term)
    var fetch_url = base_url + term +'"';
    var headers = new Headers();
    var requestOptions = { 
        method: 'GET',
        headers: headers,
        mode: 'cors',
        cache: 'default' 
    };

    fetch(fetch_url,requestOptions)
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {

            if("Error" in data){
                alert(data['Error'])
            }else{
                for(var i = 0; i < data.length;i++){
                    addMarker(data[i]["tweet_location"]["lat"],data[i]["tweet_location"]["lng"],data[i]["tweet_text"],data[i]["tweet_screen_name"],data[i]["tweet_id"]);
                    console.log(data);
                }
            }
        })
        .then(function(){
            document.getElementById('submit').disabled = false;
        })
        .catch(function(error){
            document.getElementById('submit').disabled = false;
            alert("Unable to search using that term. Please try a different term and resubmit.");
        });
}


createMap();

//Check to see if the form is filled out correctly and clear the layers in case there was any previous markers
document.getElementById('submit').addEventListener("click", function(){
    checkForm();
    layerGroup.clearLayers();
});
