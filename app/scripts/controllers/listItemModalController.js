'use strict';

/**
* This method closes the modal
*/
angular.module('h4hApp').controller('ListItemModalController', function($scope, $http, close, item_type_id, owner_id) {
  $scope.close = function(result) {  
    close(result, 500); // close, but give 500ms for bootstrap to animate
  };

  $scope.listItem = function(){
    //$scope.fromTime=$('#rentRequestFromDateTimepicker1 input').val();
    //$scope.toTime=$('#rentRequestToDateTimepicker1 input').val();

    //$scope.meetupAt = $('#Autocomplete').val();
    console.log("Daily rate set at $" + $scope.dailyRate);//"Here in request Item modal, fromtime: " + $scope.fromTime+", itemDuration: "
    	//+$scope.duration+", dailyRate: $"+daily_rate + ", totalCost: "+$scope.cost+", itemID: "+ item_id+ ", renteeID: "+rentee_id);
    var dataObj = {
      item_type_id: item_type_id,
      user_id: owner_id,
      daily_rate: $scope.dailyRate, 
    };
    console.log(dataObj);	
    var res = $http.post(server_url + 'item', dataObj);
    res.success(function(data, status, headers, config) {
      $scope.message = data;
    });
    res.error(function(data, status, headers, config) {
      alert( "failure message: " + JSON.stringify({data: data}));
    });
  }
});

