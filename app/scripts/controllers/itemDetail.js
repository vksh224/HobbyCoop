'use strict';

/**
 * @ngdoc function
 * @name h4hApp.controller:ItemDetailCtrl
 * @description
 * # ItemDetailCtrl
 * Controller of the h4hApp
 */

angular.module('h4hApp')
  .controller('ItemDetailCtrl', ['$scope', '$routeParams', function($scope, $routeParams) {
    var items = [
      {
        image: "images/car.jpg",
        price: 20000,
        location: "St. Louis",
        title: "CAR 1",
        description: "Lorem ipsum dolor sit amet, quo inermis quaerendum ea. Ea doctus option tamquam eam. Ea platonem maluisset eos. Audire consulatu cum et. Id mel prima theophrastus reprehendunt. Ius no propriae omittantur mediocritatem."
      },
      {
        image: "images/car.jpg",
        price: 80000,
        location: "New Jersey",
        title: "CAR 2",
        description: "Lorem ipsum dolor sit amet, quo inermis quaerendum ea. Ea doctus option tamquam eam. Ea platonem maluisset eos. Audire consulatu cum et. Id mel prima theophrastus reprehendunt. Ius no propriae omittantur mediocritatem."
      }
    ];

    $scope.item = items[$routeParams.id - 1];
  }]);
