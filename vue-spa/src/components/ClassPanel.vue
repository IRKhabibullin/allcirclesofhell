<template>
    <b-card-body class="p-2">
        <b-list-group>
            <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                Health
                <b-badge variant="primary" pill>{{ hero.health }}</b-badge>
            </b-list-group-item>
            <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                Damage
                <b-badge variant="primary" pill>{{ hero.damage }}</b-badge>
            </b-list-group-item>
            <b-list-group-item class="border-0 p-0 d-flex justify-content-between align-items-center">
                Armor
                <b-badge variant="primary" pill>{{ hero.armor }}</b-badge>
            </b-list-group-item>
        </b-list-group>
        <b-row>
            <b-col md="6" v-b-tooltip.hover v-bind:title="hero.suit.description">
                <b-card-img v-bind:src="hero.suit.img_path" class="rounded-0"></b-card-img>
                <b-card-text>{{ hero.suit.name }}</b-card-text>
            </b-col>
            <b-col md="6" v-b-tooltip.hover v-bind:title="hero.weapon.description">
                <b-card-img v-bind:src="hero.weapon.img_path" class="rounded-0"></b-card-img>
                <b-card-text>{{ hero.weapon.name }}</b-card-text>
            </b-col>
        </b-row>
    </b-card-body>
</template>

<script>

  export default {
    props: {
      hero: Object
    }
  }
</script>

<style lang="scss">
  .vital-bars {
    height: 100%;
    width: 100%;
  }

  .circle-bar {
    margin: 0 0.25em;
    height: 50px;
    width: 50px;
    vertical-align: middle;
    line-height: 50px;
    font-size: 20px;
    color: black;
    border-radius: 100%;
    text-align: center;
    position: relative;
  }

  #hp-bar {
    background: #ff0000;
  }

  #armor-bar {
    background: #a8bdbc;
  }

  #dmg-bar {
    background: #6e7dda;
  }

  .bar-value {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }
</style>
