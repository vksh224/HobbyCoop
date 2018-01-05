'use strict';

/**
 * @ngdoc function
 * @name h4hApp.controller:CreateAccountCtrl
 * @description
 * # CreateAccountCtrl
 * Controller of the h4hApp
 */
angular.module('h4hApp')
  .controller('CreateAccountCtrl', ['$scope', '$http', 'UserService', function($scope, $http, UserService) {
    $scope.submit = function(valid) {
      if(valid) {
        $scope.user.lat = $scope.locationDetails.geometry.location.H;
        $scope.user.lon = $scope.locationDetails.geometry.location.L;
        $http.post(server_url + 'register', $scope.user)
          .success(function(data, status, headers, config) {
            if(data.status !== "Error") {
              UserService.setUserId($scope.user.email, data.user_id);
              console.log('user ' + data.user_id + ' logged on');
            }
            else {
              $scope.error = true;
            }
          })
          .error(function() {
            $scope.error = true;
            console.log('error upon account creation');
          });
        }
      };

  }]);
