<template>
    <b-card-body class="p-2 text-outline" body-bg-variant="transparent">
        <b-list-group>
            <b-list-group-item class="bg-transparent border-0 p-0 d-flex justify-content-between align-items-center">
                Health
                <b-badge variant="primary" pill>{{ hero.health }}</b-badge>
            </b-list-group-item>
            <b-list-group-item class="bg-transparent border-0 p-0 d-flex justify-content-between align-items-center">
                Damage
                <b-badge variant="primary" pill>{{ hero.damage }}</b-badge>
            </b-list-group-item>
            <b-list-group-item class="bg-transparent border-0 p-0 d-flex justify-content-between align-items-center">
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
