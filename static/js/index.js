function initMap() {
    var uluru = {lat: 34.025126, lng: -118.4815078};
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 14,
      center: uluru
    });
    var marker = new google.maps.Marker({
      position: uluru,
      map: map
    });
    var marker2 = new google.maps.Marker({
      position: {lat: 34.035126, lng: -118.4915078},
      map: map
    });
}

$(document).ready(function(){

    fp_config = {
        enableTime: true,
        altInput: true,
        minDate: "today"
    }

    var user_action_box_original = `
        <div class="btn-group mb-2" role="group">
          <button type="button" class="btn btn-outline-primary active" id="search">Search parking</button>
          <button type="button" class="btn btn-outline-primary" id="host">Host parking</button>
        </div>
        <div class="input-group mb-1">
          <input type="text" class="form-control" placeholder="Enter address" id="parking_address">
          <div class="input-group-append">
            <button class="btn btn-outline-secondary search" type="button" id="action_btn">Search</button>
          </div>
        </div>
    `

    var user_action_box_datepick = `
        <div class="input-group mb-1">
          <div class="input-group-prepend">
            <span class="input-group-text">From</span>
          </div>
          <input class="parking_datetime_input" type="text" class="form-control" placeholder="Select...">
        </div>
        <div class="input-group mb-2">
          <div class="input-group-prepend">
            <span class="input-group-text">Until</span>
          </div>
          <input class="parking_datetime_input" type="text" class="form-control" placeholder="Select...">
        </div>
        <div class="btn-group mb-0" role="group">
          <button type="button" class="btn btn-outline-primary" id="cancel_search">Cancel</button>
          <button type="button" class="btn btn-outline-primary" id="perform_search">Search</button>
        </div>
    `

    setupAutocomplete()


    // EVENT LISTENERS

    $(document).on("click", ".btn-group > .btn", function() {
        $(".btn-group > .btn").removeClass("active");
        $(this).addClass("active");
    });
    $(document).on("click", ".btn-group > .btn#host", function(){
        $("#action_btn").html("Add").removeClass("search").addClass("add")
    });
    $(document).on("click", ".btn-group > .btn#search", function(){
        $("#action_btn").html("Search").removeClass("add").addClass("search")
    });

    $(document).on("click", "#cancel_search", function() {
        $("#user_action_box").children().each(function() {
            $(this).remove()
        })
        $("#user_action_box").html(user_action_box_original)
        setupAutocomplete()
    })

    $(document).on("click", "#perform_search", function() {
        // perform search
    })

    // FUNCTION DEFINITIONS

    function setupAutocomplete() {
        var input = document.getElementById('parking_address');
        var options = {
            types: ['address']
        };
        autocomplete = new google.maps.places.Autocomplete(input, options);
        autocomplete.addListener('place_changed', addressSelected);
    }

    function addressSelected() {
        var action_btn_original_text = $("#action_btn").html();
        $("#action_btn").html("<i class='fa fa-circle-o-notch fa-spin'></i>")
        var address_url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + $("#parking_address").val().split(' ').join('+')
        $.get(address_url, function(response) {
            if (response.status == "OK") {
                var lat = response.results[0]["geometry"]["location"]["lat"]
                var long = response.results[0]["geometry"]["location"]["lng"]
                var formatted_address = response.results[0]["formatted_address"]
                var short_address_length = getPosition(formatted_address, ",", 2)
                var short_address = formatted_address.slice(0, short_address_length)

                if ($("#action_btn").hasClass("search")) {

                    $("#user_action_box").children().each(function() {
                        $(this).remove()
                    })

                    $("#user_action_box").html("<div class='mb-2'>Find parking near:<br/>"+short_address+"</div>"+user_action_box_datepick)

                    flatpickr(".parking_datetime_input", fp_config);



                }
                if ($("#action_btn").hasClass("add")) {

                }
            } else {
                alert("Please enter a valid address")
                $("#action_btn").html(action_btn_original_text)
            }
        })

    }

    function getPosition(string, subString, index) {
        return string.split(subString, index).join(subString).length;
    }
});