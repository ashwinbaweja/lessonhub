// Load the application once the DOM is ready, using `jQuery.ready`:
$(function(){

  // Curriculum Model
  // ----------

  // Our basic **Curriculum** model has `title`, `subtitle`, `duration`, `subject` and `updated` attributes.
  window.Curriculum = Backbone.Model.extend({

    idAttribute: "_id",

    // If you don't provide a curriculum, one will be provided for you.
    EMPTY: "no curriculum available",

    // Ensure that each curriculum created has `content`.
    initialize: function() {
      if (!this.get("title")) {
        this.set({"title": this.EMPTY});
      }
    },


    // Remove this Curriculum from *localStorage* and delete its view.
    clear: function() {
      this.destroy();
      this.view.remove();
    }

  });

  // Curriculum Collection
  // ---------------Ï
  window.CurriculumList = Backbone.Collection.extend({

    // Reference to this collection's model.
    model: Curriculum,

    url: '/user/' + $("#userid"),

    // We keep the Curriculum in sequential order, despite being saved by unordered
    // GUID in the database. This generates the next order number for new items.
    nextOrder: function() {
      if (!this.length) return 1;
      return this.last().get('order') + 1;
    },

    // Curriculum are sorted by their original insertion order.
    comparator: function(curriculum) {
      return curriculum.get('order');
    }

  });

  // Create our global collection of **Curriculum**.
  window.Curriculums = new CurriculumList;

  // Curriculum Item View
  // --------------

  // The DOM element for a curriculum item...
  window.CurriculumView = Backbone.View.extend({

    //... is a list tag.
    tagName:  "li",

    // Cache the template function for a single item.
    template: _.template($('#curriculum-template').html()),

    // The DOM events specific to an item.
    events: {
      "dblclick div.curriculum-content" : "edit",
      "keypress .curriculum-input"      : "updateOnEnter"
    },

    // The CurriculumView listens for changes to its model, re-rendering. Since there's
    // a one-to-one correspondence between a **Curriculum** and a **View** in this
    // app, we set a direct reference on the model for convenience.
    initialize: function() {
      _.bindAll(this, 'render', 'close');
      this.model.bind('change', this.render);
      this.model.view = this;
    },

    // Re-render the contents of the curriculum item.
    render: function() {
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    },

    // Switch this view into `"editing"` mode, displaying the input field if we choose to make this editable
    edit: function() {
      $(this.el).addClass("editing");
      this.input.focus();
    },

    // Close the `"editing"` mode, saving changes to the curriculum.
    close: function() {
      this.model.save({content: this.input.val()});
      $(this.el).removeClass("editing");
    },

    // If you hit `enter`, we're through editing the curriculum.
    //
    updateOnEnter: function(e) {
      if (e.keyCode == 13) this.close();
    },

    // Remove this view from the DOM.
    remove: function() {
      $(this.el).remove();
    },

    // Remove the item, destroy the model.
    clear: function() {
      this.model.clear();
    }

  });

  // The Application
  // ---------------

  // Our overall **AppView** is the top-level piece of UI.
  window.AppView = Backbone.View.extend({

    // Instead of generating a new element, bind to the existing skeleton of
    // the App already present in the HTML.
    el: $("#curriculumapp"),

    // Our template for the line of statistics at the bottom of the app.
    statsTemplate: _.template($('#stats-template').html()),

    // Delegated events for creating new items, and clearing completed ones.
    events: {
    },

    // At initialization we bind to the relevant events on the `Curriculum`
    // collection, when items are added or changed. Kick things off by
    // loading any preexisting curriculums that might be saved in *localStorage*.
    initialize: function() {
      var handlers = {
          "success": this.addAll,
          "error": function() {console.log("fetch failed")}
         };
      
      Curriculums.fetch(handlers);
    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
      this.$('#curriculum-stats').html(this.statsTemplate({
        curriculums:  Curriculums.length,
      }));
    },

    // Add a single curriculum item to the list by creating a view for it, and
    // appending its element to the `<ul>`.
    addOne: function(curriculum) {
      console.log('add one');
      var view = new CurriculumView({model: curriculum});
      this.$("#curriculum-list").append(view.render().el);
    },

    // Add all items in the **Curriculum** collection at once.
    addAll: function() {
        console.log('add all');
        Curriculums.each(this.addOne);
    },

    // Generate the attributes for a new Curriculum item.
    // `title`, `subtitle`, `duration`, `subject` and `updated` attributes.
    newAttributes: function() {
      return {
        title: this.input.val(),
        subtitle:   Curriculum.nextOrder(),
        duration: "",
        subject: "",
        updated: "",
      };
    },

    // If you hit return in the main input field, create new **Curriculum** model,
    // persisting it to *localStorage*.
    createOnEnter: function(e) {
      if (e.keyCode != 13) return;
      Curriculum.create(this.newAttributes());
      this.input.val('');
    },

    // Clear all finished Curriculum items, destroying their models.
    // hypothetical
    // clearCompleted: function() {
    //   _.each(Curriculum.deleted, function(curriculum){ curriculum.clear(); });
    //   return false;
    // },

  });

  // Finally, we kick things off by creating the **App**.
  window.App = new AppView;

});
