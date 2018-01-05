'use strict';

myApp.controller("SearchCtrl",function ($scope) {

    $scope.searchWord="";
    $scope.result1 = '';
    $scope.options1 = null;
    $scope.details1 = '';



    $scope.result2 = '';
    $scope.options2 = {
      country: 'ca',
      types: '(cities)'
    };    $scope.details2 = '';



    $scope.result3 = '';
    $scope.options3 = {
      country: 'gb',
      types: 'establishment'
    };
    $scope.details3 = '';

  });

myApp.controller("HeaderCtrl",['$scope','ModalService','ItemService','$http','$location','UserService',
  function ($scope, ModalService, ItemService, $http, $location, UserService) {

    $scope.user_id = UserService.getUserId();

    $scope.$watch(function () { return UserService.getUserId() }, function (newVal, oldVal) {
        $scope.user_id = UserService.getUserId();
    });

    $scope.showCategory = function(){
      $("#nav_category").show();
    };
    $scope.closeCategory = function(){
      $("#nav_category").hide();
    };
    $scope.searchItem = function(){
        ItemService.setItems($scope.searchText);
        $location.path('/searchResults');
    };
    $scope.searchCategory = function(categoryName){
        console.log("Search category is "  +categoryName);
        ItemService.setItems(categoryName);
        $location.path('/searchResults');
    };
    $scope.signInModal = function() {
        ModalService.showModal({
            templateUrl: 'modals/signInModal.html',
            controller: "SignInModalController"
        }).then(function(modal) {
            modal.element.modal();
            modal.close.then(function(result) {
                $scope.message = "You said " + result;
            });
        });
    };

    $scope.logout = UserService.logout;

    $scope.itemsList = ["item3"];

  	$scope.categoryList = [];
    $scope.autoCompleteList = [];

    //get Category List
    $http({
      method: 'GET',
      url: server_url + 'categories'
    })
    .success(function (data, status, headers, config) {
      $scope.categoryList = data;
      //console.log("THe category list: "+$scope.categoryList);
      angular.forEach(data, function(category, index) {
         //console.log("Category name "+ category.name);
         $scope.autoCompleteList.push(category.name);
      });
    })
    .error(function (data, status, headers, config) {
    // something went wrong :(
    });

  }]);
