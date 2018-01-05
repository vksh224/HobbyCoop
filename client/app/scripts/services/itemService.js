'use strict';


/**
*https://uncorkedstudios.com/blog/multipartformdata-file-upload-with-angularjs
**/

angular.module('h4hApp').factory('ItemService', function($http,$q) {
  var itemsList = [];
  var categoryList =[];
  var searchResults = [];
  return {
    setItems : function(searchText){
      var deferred = $q.defer();
      searchResults = [];
      //var collectiveItemsList = [];
      $http({
        method: 'GET',
        //url : 'scripts/controllers/searchItems.json'
        url: server_url + 'search/'+searchText
        //params: {searchText: searchText}
      }).success(function (response) {
        deferred.resolve(response);
        var data = response;

        angular.forEach(data, function(category) {
          // console.log(category.name +"  " + searchText +"  "+ category.name.toLowerCase().indexOf(searchText.toLowerCase()));
          if( category.name.toLowerCase().indexOf(searchText.toLowerCase()) >= 0 ) {
            //console.log(category);
            searchResults.push(category);
          }
        });
                           
      }).error(function (response) {
        deferred.reject(response);
      });

      return deferred.promise;
    },
    getItems : function(){
      return itemsList;
    },

    getCategories : function(){
      return categoryList;
    },

    getSearchResults : function(){
      return searchResults;
    },

    requestReturnItem : function(userId, itemId){
      var deferred = $q.defer();
      console.log("Here in request return item modal " + userId+ "  "+itemId);
      var dataObj = {
        user_id: itemId,
        transaction_id: itemId
      };  
      var res = $http.post(
        server_url + 'requestReturnItem',
        dataObj
      );
      res.success(function(data, status, headers, config) {
        deferred.resolve(data);
        //console.log(data);
        //$scope.message = data;
        userId = data.user_id;
        // $location.path('/myAccount');
      });
      res.error(function(data, status, headers, config) {
        deferred.reject(data);
      });
      //REMOVE BELOW TWO LINES
      return deferred.promise;
    },
    confirmItemPickup : function(userId, itemId){
      var deferred = $q.defer();
      console.log("Here in sign In modal " + userId+ "  "+itemId);
      var dataObj = {
        user_id: itemId,
        item_request_id: itemId
      };
      var res = $http.post(
        server_url + 'confirmItemPickup',
         dataObj
      );
      res.success(function(data, status, headers, config) {
        deferred.resolve(data);
        //console.log(data);
        //$scope.message = data;
        userId = data.user_id;
        // $location.path('/myAccount');
      });
      res.error(function(data, status, headers, config) {
        deferred.reject(data);
      });
      //REMOVE BELOW TWO LINES
      return deferred.promise;
    },

    confirmItemReturn : function(userId, itemId){
      var deferred = $q.defer();
      console.log("Here in confirm item pickup modal " + userId+ "  "+itemId);
      var dataObj = {
        return_time_id: itemId
      };
      var res = $http.post(
        server_url + 'confirmItemReturn',
         dataObj
      );
      res.success(function(data, status, headers, config) {
        deferred.resolve(data);
        //console.log(data);
        //$scope.message = data;
        userId = data.user_id;
        // $location.path('/myAccount');
      });
      res.error(function(data, status, headers, config) {
        deferred.reject(data);
      });
      //REMOVE BELOW TWO LINES
      return deferred.promise;
    },

    deleteItem : function(userId, itemId){
      var deferred = $q.defer();
      var dataObj = {
        item_id: itemId,
        user_id: userId,
      };
      var res = $http.delete(
        server_url + 'item/'+itemId,
         dataObj
      );
      res.success(function(data, status, headers, config) {
        deferred.resolve(data);
        //console.log(data);
        //$scope.message = data;
        userId = data.user_id;
        // $location.path('/myAccount');
      });
      res.error(function(data, status, headers, config) {
        deferred.reject(data);
      });
      //REMOVE BELOW TWO LINES
      return deferred.promise;
    }
  }
});

